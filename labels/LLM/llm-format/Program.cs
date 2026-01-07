using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using DuckDB.NET.Data;
using LLama;
using LLama.Common;
using LLama.Native;

public class Program
{
    // 1. Configuration
    const string HuggingFaceRepo = "nomic-ai/nomic-embed-text-v1.5-GGUF";
    const string ModelFileName = "nomic-embed-text-v1.5.f16.gguf";
    const string ModelPath = "./model";
    const string DbPath = "data/ClassifiedCompaniesRelational.duckdb";
    const string OutputDbPath = "data/output_test.duckdb";
    const string SourceTableName = "ClassifiedCompaniesRelational";
    const string DestTableName = "companies_with_embeddings";
    const string TextColumnName = "CompanyName";
    const string IdColumnName = "CompanyNumber";
    const int TotalRows = 1000; // Set to -1 to process all rows
    const int BatchSize = 500;
    const int EmbeddingDimension = 128; // Target dimension

    public static async Task Main(string[] args)
    {
        // Suppress verbose llama.cpp logging
        NativeLibraryConfig.Instance.WithLogCallback((level, message) =>
        {
            // Only log errors, suppress all info/debug/warning messages
            if (level == LLamaLogLevel.Error)
            {
                Console.Error.WriteLine($"[Error] {message}");
            }
        });

        Console.WriteLine("Starting embedding process...");

        // Ensure model directory exists
        Directory.CreateDirectory(ModelPath);
        string fullModelPath = Path.Combine(ModelPath, ModelFileName);

        // 2. Download the model if it doesn't exist
        await ModelManager.DownloadModel(HuggingFaceRepo, ModelFileName, fullModelPath);

        // 3. Initialize the embedding service
        using var embeddingService = new EmbeddingService(fullModelPath, EmbeddingDimension);

        // 4. Perform single text embedding example
        string sampleText = "This is a test sentence for embedding.";
        float[] sampleEmbedding = await embeddingService.GenerateEmbedding(sampleText);
        Console.WriteLine($"Generated embedding for sample text with dimension: {sampleEmbedding.Length}");
        Console.WriteLine($"First 5 values: {string.Join(", ", sampleEmbedding.Take(5))}");


        // 5. Perform batch embedding for DuckDB
        await ProcessDuckDb(embeddingService);

        Console.WriteLine("Embedding process finished.");
    }

    private static async Task ProcessDuckDb(EmbeddingService embeddingService)
    {
        Console.WriteLine("\nStarting DuckDB processing...");

        // Ensure output directory exists
        string outputDir = Path.GetDirectoryName(OutputDbPath);
        if (!string.IsNullOrEmpty(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }

        // Open connection to input database for reading
        using var inputConnection = new DuckDBConnection($"Data Source={DbPath}");
        inputConnection.Open();

        // Open connection to output database for writing
        using var outputConnection = new DuckDBConnection($"Data Source={OutputDbPath}");
        outputConnection.Open();

        // Create or clear the destination table in output database
        using (var cmd = outputConnection.CreateCommand())
        {
            cmd.CommandText = $"CREATE OR REPLACE TABLE {DestTableName} (CompanyNumber VARCHAR, CompanyName VARCHAR, embedding FLOAT[{EmbeddingDimension}]);";
            cmd.ExecuteNonQuery();
        }

        long totalRows = GetTotalRows(inputConnection);
        long rowsToProcess = (TotalRows > 0 && TotalRows < totalRows) ? TotalRows : totalRows;

        Console.WriteLine($"Processing {rowsToProcess} rows from '{SourceTableName}' in '{DbPath}'...");
        Console.WriteLine($"Writing results to '{OutputDbPath}'...");

        for (int offset = 0; offset < rowsToProcess; offset += BatchSize)
        {
            using (var timer = new SimpleTimer($"Processing batch from offset {offset}").Start())
            {
                // Step 1: Read raw batch data from database
                var batchData = ReadBatchRaw(inputConnection, offset, BatchSize);
                timer.Track("sql_read");

                if (batchData.Count == 0) break;

                // Step 2: Extract and process raw data into separate ID and text lists
                var (idBatch, textBatch) = ProcessBatchData(batchData);
                timer.Track("processing");

                // Step 3: Generate embeddings
                var embeddings = await embeddingService.GenerateEmbeddings(textBatch);
                timer.Track("embedding");

                // Step 4: Write results to output database
                await InsertBatch(outputConnection, idBatch, textBatch, embeddings);
                timer.Track("db_write_bulk");
            }
        }

        Console.WriteLine($"DuckDB processing finished. Output saved to '{OutputDbPath}'.");
    }

    private static long GetTotalRows(DuckDBConnection connection)
    {
        using var cmd = connection.CreateCommand();
        cmd.CommandText = $"SELECT COUNT(*) FROM {SourceTableName}";
        return (long)(cmd.ExecuteScalar() ?? 0L);
    }

    private static List<(string id, string text)> ReadBatchRaw(DuckDBConnection connection, int offset, int limit)
    {
        var batchData = new List<(string id, string text)>();
        using var cmd = connection.CreateCommand();
        cmd.CommandText = $"SELECT {IdColumnName}, {TextColumnName} FROM {SourceTableName} ORDER BY {IdColumnName} ASC LIMIT {limit} OFFSET {offset};";
        using var reader = cmd.ExecuteReader();
        while (reader.Read())
        {
            batchData.Add((reader.GetString(0), reader.GetString(1)));
        }
        return batchData;
    }

    private static (List<string> ids, List<string> texts) ProcessBatchData(List<(string id, string text)> batchData)
    {
        var ids = new List<string>();
        var texts = new List<string>();
        foreach (var row in batchData)
        {
            ids.Add(row.id);
            texts.Add(row.text);
        }
        return (ids, texts);
    }

    private static async Task InsertBatch(DuckDBConnection connection, List<string> ids, List<string> texts, List<float[]> embeddings)
    {
        using var transaction = connection.BeginTransaction();
        for(int i = 0; i < ids.Count; i++)
        {
            using var cmd = connection.CreateCommand();
            var embeddingString = $"[{string.Join(", ", embeddings[i])}]";
            cmd.CommandText = $"INSERT INTO {DestTableName} VALUES (?, ?, {embeddingString});";
            cmd.Parameters.Add(new DuckDBParameter(ids[i]));
            cmd.Parameters.Add(new DuckDBParameter(texts[i]));
            await cmd.ExecuteNonQueryAsync();
        }
        transaction.Commit();
    }
}

public static class ModelManager
{
    public static async Task DownloadModel(string repo, string modelFile, string destPath)
    {
        if (File.Exists(destPath))
        {
            Console.WriteLine("Model already exists. Skipping download.");
            return;
        }

        Console.WriteLine($"Downloading model '{modelFile}' from '{repo}'...");
        string url = $"https://huggingface.co/{repo}/resolve/main/{modelFile}";

        using var client = new HttpClient();
        using var response = await client.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();

        long? totalBytes = response.Content.Headers.ContentLength;

        using var contentStream = await response.Content.ReadAsStreamAsync();
        using var fileStream = new FileStream(destPath, FileMode.Create, FileAccess.Write, FileShare.None, 8192, true);

        var buffer = new byte[8192];
        long downloadedBytes = 0;
        int bytesRead;
        while ((bytesRead = await contentStream.ReadAsync(buffer, 0, buffer.Length)) > 0)
        {
            await fileStream.WriteAsync(buffer, 0, bytesRead);
            downloadedBytes += bytesRead;

            if (totalBytes.HasValue)
            {
                double percentage = (double)downloadedBytes / totalBytes.Value * 100;
                Console.Write($"\rDownloading: {downloadedBytes / 1024 / 1024:F2} MB / {totalBytes.Value / 1024 / 1024:F2} MB ({percentage:F2}%)");
            }
            else
            {
                 Console.Write($"\rDownloading: {downloadedBytes / 1024 / 1024:F2} MB");
            }
        }
        Console.WriteLine("\nDownload complete.");
    }
}

public class EmbeddingService : IDisposable
{
    private readonly LLamaEmbedder _embedder;
    private readonly LLamaWeights _weights;
    private readonly int _embeddingDimension;

    public EmbeddingService(string modelPath, int embeddingDimension)
    {
        var parameters = new ModelParams(modelPath)
        {
            ContextSize = 8192,      // Match nomic-embed model context size
            BatchSize = 8192,        // Enable large batch processing at token level
            UBatchSize = 8192,       // Must equal BatchSize for non-causal (embedding) models
            GpuLayerCount = 999,     // Offload ALL layers to GPU
            Embeddings = true,
        };
        _weights = LLamaWeights.LoadFromFile(parameters);
        _embedder = new LLamaEmbedder(_weights, parameters);
        _embeddingDimension = embeddingDimension;
    }

    public async Task<float[]> GenerateEmbedding(string text)
    {
        // Nomic models require a prefix for optimal performance.
        string prefixedText = "search_document: " + text;

        // The call to GetEmbeddings is asynchronous and returns IReadOnlyList<float[]>
        var embeddingsList = await _embedder.GetEmbeddings(prefixedText);
        float[] embedding = embeddingsList[0];

        // The nomic model supports variable dimensionality, but LLamaSharp does not directly expose this.
        // As a workaround, we truncate the embedding to the desired dimension.
        if (embedding.Length > _embeddingDimension)
        {
            float[] truncatedEmbedding = new float[_embeddingDimension];
            Array.Copy(embedding, truncatedEmbedding, _embeddingDimension);
            return truncatedEmbedding;
        }
        return embedding;
    }

    public async Task<List<float[]>> GenerateEmbeddings(List<string> texts)
    {
        // LLamaSharp doesn't expose batch API well, so we still process sequentially
        // However, with increased BatchSize and ContextSize, each call should be faster
        var results = new List<float[]>();
        foreach (var text in texts)
        {
            var embedding = await GenerateEmbedding(text);
            results.Add(embedding);
        }
        return results;
    }

    public void Dispose()
    {
        _embedder.Dispose();
        _weights.Dispose();
    }
}
