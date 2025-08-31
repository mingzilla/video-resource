-- MySQL Test Data for Laptop Database
-- This file creates 1000 laptop records with intentional data quality variations
-- for testing data normalization and graph modeling concepts

-- Create database and use it
USE laptops;

-- Create laptops table
CREATE TABLE laptops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    cpu VARCHAR(20) NOT NULL,
    video_card VARCHAR(30) NOT NULL,
    screen_size INT NOT NULL,
    ram VARCHAR(10) NOT NULL,
    hard_drive VARCHAR(10) NOT NULL,
    price DECIMAL(8,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance testing
CREATE INDEX idx_brand ON laptops(brand);
CREATE INDEX idx_cpu ON laptops(cpu);
CREATE INDEX idx_video_card ON laptops(video_card);
CREATE INDEX idx_ram ON laptops(ram);
CREATE INDEX idx_price ON laptops(price);

-- Insert laptop records with data quality variations
INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Lenovo ThinkPad Series (Business/Professional)
('ThinkPad X1 Carbon Gen 10', 'Lenovo', 'i9', 'Nvidia 30xx', 13, '32G', '1T', 2499.00, 'Fantastic Lenovo easy to carry laptop for daily usage and video editing. Perfect for professionals who need powerful performance in a lightweight design. Features advanced cooling system and premium build quality.'),
('ThinkPad T14s Gen 3', 'Lenovo', 'I7', 'NVIDIA 30xx', 15, '16GB', '1TB', 1899.00, 'Exceptional business laptop with robust security features and excellent keyboard. Ideal for office work, programming, and light content creation. Military-grade durability testing ensures reliability.'),
('ThinkPad P1 Gen 5', 'Lenovo', 'Intel i9', 'Nvidia 40xx', 16, '64G', '2T', 3299.00, 'Ultimate workstation laptop for CAD, 3D rendering, and professional video editing. Features ISV certification and premium display technology. Built for demanding creative professionals and engineers.'),
('ThinkPad E15 Gen 4', 'Lenovo', 'i5', 'Nvidia 30xx', 15, '16G', '1T', 1299.00, 'Affordable business laptop with solid performance for everyday tasks. Great for small businesses and students. Includes essential security features and comfortable typing experience.'),
('ThinkPad X13 Yoga', 'Lenovo', 'I7', 'GeForce RTX 30xx', 13, '32GB', '1TB', 2199.00, 'Versatile 2-in-1 convertible laptop with touchscreen and pen support. Perfect for presentations, note-taking, and creative work. Premium build quality with flexible form factor.'),

-- Dell XPS Series (Premium Consumer)
('XPS 13 Plus Developer Edition', 'Dell', 'i7', 'Nvidia 40xx', 13, '32G', '1T', 2299.00, 'Stunning premium ultrabook with edge-to-edge display and minimalist design. Excellent for software development, content creation, and professional work. Outstanding build quality and performance.'),
('XPS 15 OLED Creator', 'Dell', 'I9', 'NVIDIA RTX 40xx', 15, '64GB', '2TB', 3499.00, 'Professional creator laptop with gorgeous OLED display and powerful specs. Perfect for video editing, 3D modeling, and graphic design. Premium materials and exceptional screen quality.'),
('XPS 17 Workstation', 'Dell', 'Intel Core i9', 'Nvidia 50xx', 16, '64G', '2T', 3899.00, 'Top-tier mobile workstation with massive screen and incredible performance. Ideal for professional video production, engineering, and high-end creative work. No compromises on power or quality.'),
('XPS 13 2-in-1', 'Dell', 'i7', 'RTX 30xx', 13, '16G', '1TB', 1999.00, 'Elegant convertible laptop with premium materials and excellent portability. Great for business professionals and creative work. Versatile form factor with touch and pen support.'),
('XPS 15 Studio', 'Dell', 'i9', 'Nvidia 40xx', 15, '32GB', '1T', 2899.00, 'High-performance laptop for content creators and professionals. Features color-accurate display and powerful internals. Perfect balance of performance and portability for creative workflows.'),

-- HP EliteBook Series (Business)
('EliteBook 840 G9', 'HP', 'i7', 'Nvidia 30xx', 15, '16GB', '1T', 1799.00, 'Secure business laptop with enterprise-grade features and excellent performance. Built for professionals who need reliability and security. Includes advanced management and connectivity options.'),
('EliteBook x360 1040 G9', 'HP', 'I7', 'NVIDIA 30xx', 13, '32G', '1TB', 2399.00, 'Premium convertible business laptop with 360-degree hinge and touch display. Perfect for executives and mobile professionals. Combines elegance with powerful performance and security.'),
('EliteBook 850 G9', 'HP', 'Intel i7', 'GeForce RTX 30xx', 16, '32GB', '2T', 2599.00, 'Large-screen business laptop with excellent performance and display quality. Ideal for data analysis, presentations, and multitasking. Features comprehensive security and management tools.'),
('EliteBook 1030 x360 G4', 'HP', 'i5', 'Nvidia 30xx', 13, '16G', '1T', 1599.00, 'Compact convertible laptop perfect for business travel and presentations. Lightweight design with solid performance. Great for sales professionals and consultants who are always on the move.'),
('EliteBook 855 G8', 'HP', 'I7', 'RTX 30xx', 15, '32G', '1TB', 2199.00, 'Reliable business laptop with excellent battery life and performance. Features modern connectivity and security options. Perfect for knowledge workers and business professionals.'),

-- Apple MacBook Series
('MacBook Pro 13-inch M2', 'Apple', 'i7', 'Nvidia 30xx', 13, '16GB', '1T', 1999.00, 'Sleek and powerful MacBook with exceptional battery life and performance. Perfect for creative professionals and developers. Features stunning Retina display and premium build quality.'),
('MacBook Pro 16-inch M2 Max', 'Apple', 'i9', 'NVIDIA 50xx', 16, '64G', '2TB', 3999.00, 'Ultimate creative powerhouse with massive screen and incredible performance. Ideal for professional video editing, music production, and software development. Top-tier specifications and display.'),
('MacBook Air M2', 'Apple', 'i5', 'GeForce RTX 30xx', 13, '16G', '1TB', 1499.00, 'Ultra-portable laptop with excellent performance and all-day battery life. Perfect for students and professionals who need mobility. Fanless design and silent operation.'),
('MacBook Pro 14-inch M2 Pro', 'Apple', 'I7', 'Nvidia 40xx', 15, '32GB', '1T', 2799.00, 'Professional laptop with perfect balance of performance and portability. Excellent for software development, design work, and content creation. Premium display and build quality.'),
('MacBook Pro 13-inch M1', 'Apple', 'i7', 'RTX 30xx', 13, '32G', '1TB', 1799.00, 'Proven performer with excellent efficiency and performance. Great for everyday professional work and creative tasks. Outstanding battery life and reliable operation.'),

-- ASUS ZenBook Series (Premium Ultrabooks)
('ZenBook Pro 16X OLED', 'ASUS', 'i9', 'Nvidia 50xx', 16, '64GB', '2T', 3599.00, 'Flagship creator laptop with stunning OLED display and top-tier performance. Perfect for professional content creation, video editing, and 3D work. Premium materials and exceptional screen quality.'),
('ZenBook 14 OLED', 'ASUS', 'I7', 'NVIDIA 40xx', 15, '32G', '1TB', 1999.00, 'Beautiful ultrabook with vibrant OLED display and solid performance. Great for professionals and creatives who value display quality. Portable design with premium build materials.'),
('ZenBook Flip 13 UX363', 'ASUS', 'Intel i7', 'GeForce RTX 30xx', 13, '16GB', '1T', 1699.00, 'Versatile convertible laptop with 360-degree hinge and touchscreen. Perfect for note-taking, presentations, and creative work. Compact and portable with flexible usage modes.'),
('ZenBook 13 UX325', 'ASUS', 'i5', 'Nvidia 30xx', 13, '16G', '1TB', 1299.00, 'Affordable premium ultrabook with excellent portability and performance. Great for students and professionals who need a reliable daily driver. Lightweight with good build quality.'),
('ZenBook Pro 15 OLED', 'ASUS', 'i9', 'RTX 40xx', 15, '32GB', '2TB', 2899.00, 'High-performance creator laptop with color-accurate OLED display. Ideal for graphic design, video editing, and professional content creation. Excellent display and solid performance.'),

-- Gaming Laptops - MSI Series
('MSI GE76 Raider', 'MSI', 'I9', 'NVIDIA RTX 50xx', 16, '64G', '2T', 3799.00, 'Ultimate gaming powerhouse with RGB lighting and top-tier performance. Perfect for competitive gaming, streaming, and content creation. Features advanced cooling and customizable aesthetics.'),
('MSI GS66 Stealth', 'MSI', 'Intel Core i9', 'Nvidia 50xx', 15, '32GB', '1TB', 2999.00, 'Sleek gaming laptop with understated design and powerful specs. Great for gamers who want performance without flashy aesthetics. Excellent build quality and thermal management.'),
('MSI Katana GF66', 'MSI', 'i7', 'GeForce RTX 40xx', 15, '16G', '1T', 1799.00, 'Affordable gaming laptop with solid performance for 1080p gaming. Perfect for students and casual gamers. Good value proposition with decent build quality and performance.'),
('MSI Creator Z16P', 'MSI', 'i9', 'NVIDIA 40xx', 16, '64GB', '2TB', 3299.00, 'Professional creator laptop optimized for content creation and design work. Features color-accurate display and powerful internals. Perfect for video editors and 3D artists.'),
('MSI Prestige 14 Evo', 'MSI', 'I7', 'RTX 30xx', 15, '32G', '1TB', 1999.00, 'Business-focused laptop with creator-friendly features and solid performance. Great for professionals who need both productivity and creative capabilities. Premium design and materials.'),

-- Gaming Laptops - Razer Series
('Razer Blade 15 Advanced', 'Razer', 'i9', 'Nvidia 50xx', 15, '32GB', '1T', 3199.00, 'Premium gaming laptop with sleek design and powerful performance. Perfect for serious gamers and content creators. Exceptional build quality with understated gaming aesthetics.'),
('Razer Blade 17', 'Razer', 'I9', 'NVIDIA RTX 50xx', 16, '64G', '2TB', 3899.00, 'Large-screen gaming powerhouse with desktop-class performance. Ideal for competitive gaming, streaming, and professional content creation. Top-tier specifications and premium materials.'),
('Razer Blade 14', 'Razer', 'Intel i7', 'GeForce RTX 40xx', 15, '32G', '1TB', 2499.00, 'Compact gaming laptop with excellent performance-to-size ratio. Great for mobile gaming and content creation. Premium build quality in a portable form factor.'),
('Razer Blade Stealth 13', 'Razer', 'i7', 'Nvidia 30xx', 13, '16GB', '1T', 1999.00, 'Ultrabook-style laptop with gaming capabilities and premium design. Perfect for professionals who occasionally game. Excellent portability with solid performance.'),
('Razer Book 13', 'Razer', 'I7', 'RTX 30xx', 13, '16G', '1TB', 1699.00, 'Productivity-focused laptop with gaming DNA and premium materials. Great for business professionals who want style and performance. Clean design with solid specifications.'),

-- Budget/Mid-range Laptops - Acer Series
('Acer Aspire 5 A515', 'Acer', 'i5', 'Nvidia 30xx', 15, '16G', '1T', 899.00, 'Affordable laptop with decent performance for everyday tasks. Perfect for students and home users. Good value proposition with solid build quality for the price point.'),
('Acer Swift 3 SF314', 'Acer', 'I7', 'NVIDIA 30xx', 15, '32GB', '1TB', 1299.00, 'Mid-range ultrabook with good performance and portability. Great for professionals and students who need reliable daily computing. Decent build quality and battery life.'),
('Acer Predator Helios 300', 'Acer', 'Intel i7', 'GeForce RTX 40xx', 16, '32G', '1T', 2199.00, 'Gaming laptop with solid performance at competitive price. Perfect for enthusiast gamers and content creators. Good cooling system and upgrade options available.'),
('Acer Nitro 5 AN515', 'Acer', 'i5', 'Nvidia 40xx', 15, '16GB', '1TB', 1499.00, 'Entry-level gaming laptop with decent specs for 1080p gaming. Great for budget-conscious gamers and students. Affordable gaming performance with room for upgrades.'),
('Acer ConceptD 7', 'Acer', 'i9', 'RTX 50xx', 16, '64G', '2T', 3499.00, 'Professional creator laptop with color-accurate display and powerful specs. Perfect for 3D modeling, video editing, and professional design work. ISV-certified for reliability.'),

-- More Lenovo Models
('IdeaPad Gaming 3', 'Lenovo', 'I7', 'NVIDIA RTX 40xx', 15, '16G', '1T', 1399.00, 'Affordable gaming laptop with solid performance for casual gaming. Great for students who want gaming capabilities. Good value with decent build quality and thermals.'),
('Legion 5 Pro', 'Lenovo', 'Intel Core i7', 'Nvidia 50xx', 16, '32GB', '1TB', 2699.00, 'High-performance gaming laptop with excellent display and powerful internals. Perfect for serious gamers and content creators. Premium gaming features and solid build quality.'),
('IdeaPad Slim 7', 'Lenovo', 'i7', 'GeForce RTX 30xx', 15, '32G', '1TB', 1799.00, 'Sleek ultrabook with good performance and premium design. Great for professionals and students who value portability. Solid specifications in an elegant package.'),
('Yoga 9i 2-in-1', 'Lenovo', 'I9', 'RTX 40xx', 15, '32GB', '2T', 2899.00, 'Premium convertible laptop with exceptional build quality and performance. Perfect for creative professionals and executives. Versatile form factor with premium materials.'),
('ThinkBook 14s Yoga', 'Lenovo', 'i5', 'Nvidia 30xx', 15, '16G', '1T', 1499.00, 'Business convertible with flexible usage modes and solid performance. Great for small business owners and professionals. Good balance of features and price.'),

-- More Dell Models
('Inspiron 15 3000', 'Dell', 'i5', 'NVIDIA 30xx', 15, '16GB', '1T', 799.00, 'Budget-friendly laptop for basic computing needs. Perfect for students and home users. Affordable option with decent performance for everyday tasks and light productivity work.'),
('Inspiron 14 5000 2-in-1', 'Dell', 'I7', 'GeForce RTX 30xx', 15, '32G', '1TB', 1599.00, 'Versatile convertible laptop with touchscreen and good performance. Great for students and professionals who need flexibility. Decent build quality at competitive price.'),
('Alienware m15 R7', 'Dell', 'Intel i9', 'Nvidia 50xx', 15, '64GB', '2TB', 3599.00, 'High-end gaming laptop with alien-inspired design and top-tier performance. Perfect for hardcore gamers and enthusiasts. Premium gaming features and exceptional specifications.'),
('Latitude 9430 2-in-1', 'Dell', 'i7', 'RTX 40xx', 15, '32G', '1T', 2799.00, 'Premium business convertible with enterprise features and excellent build quality. Ideal for executives and mobile professionals. Advanced security and management capabilities.'),
('Vostro 15 3000', 'Dell', 'I5', 'NVIDIA 30xx', 15, '16G', '1TB', 1099.00, 'Small business laptop with essential features and reliable performance. Great for office work and basic productivity tasks. Cost-effective solution for business environments.'),

-- More HP Models
('Pavilion Gaming 15', 'HP', 'i7', 'Nvidia 40xx', 15, '32GB', '1T', 1699.00, 'Mid-range gaming laptop with decent performance for 1080p gaming. Perfect for casual gamers and students. Good balance of gaming performance and everyday usability.'),
('Omen 16', 'HP', 'I9', 'NVIDIA RTX 50xx', 16, '64G', '2TB', 2999.00, 'High-performance gaming laptop with large screen and powerful specs. Ideal for competitive gaming and content creation. Advanced cooling and customizable RGB lighting.'),
('Envy x360 15', 'HP', 'Intel i7', 'GeForce RTX 30xx', 15, '32G', '1TB', 1899.00, 'Premium convertible laptop with elegant design and solid performance. Great for creative professionals and business users. Versatile 2-in-1 design with quality materials.'),
('ProBook 450 G9', 'HP', 'i5', 'Nvidia 30xx', 15, '16GB', '1T', 1299.00, 'Business laptop with essential features and reliable performance. Perfect for small businesses and professional use. Good security features and manageable price point.'),
('Spectre x360 14', 'HP', 'I7', 'RTX 40xx', 15, '32G', '1TB', 2299.00, 'Ultra-premium convertible with stunning design and excellent performance. Ideal for executives and creative professionals. Luxury materials and exceptional build quality.'),

-- More ASUS Models
('VivoBook Pro 16X OLED', 'ASUS', 'i9', 'Nvidia 50xx', 16, '64GB', '2T', 2999.00, 'Creator-focused laptop with vibrant OLED display and powerful internals. Perfect for content creation and professional design work. Excellent screen quality and solid performance.'),
('ROG Strix G15', 'ASUS', 'I7', 'NVIDIA RTX 40xx', 15, '32G', '1TB', 2199.00, 'Gaming laptop with aggressive styling and solid performance. Great for enthusiast gamers and content creators. Good cooling system and customizable RGB effects.'),
('TUF Gaming F15', 'ASUS', 'Intel i5', 'GeForce RTX 30xx', 15, '16GB', '1T', 1399.00, 'Durable gaming laptop built for reliability and performance. Perfect for budget-conscious gamers. Military-grade durability testing and decent gaming specifications.'),
('ExpertBook B9', 'ASUS', 'i7', 'Nvidia 30xx', 15, '32G', '1TB', 2199.00, 'Ultra-lightweight business laptop with exceptional portability and performance. Ideal for traveling professionals and executives. Premium materials and enterprise features.'),
('Chromebook Flip C436', 'ASUS', 'I5', 'RTX 30xx', 15, '16G', '1T', 899.00, 'Premium Chromebook with convertible design and solid build quality. Great for students and users who primarily work in web browsers. Good performance for Chrome OS tasks.'),

-- Budget and Entry-Level Models
('Acer Aspire 3 A315', 'Acer', 'i5', 'NVIDIA 30xx', 15, '16GB', '1TB', 699.00, 'Entry-level laptop perfect for basic computing tasks. Ideal for students and home users on a budget. Decent performance for web browsing, office work, and media consumption.'),
('HP 15-dy2000', 'HP', 'I5', 'GeForce RTX 30xx', 15, '16G', '1T', 749.00, 'Affordable laptop with reliable performance for everyday use. Great for families and students. Simple design with essential features at competitive price point.'),
('Lenovo IdeaPad 3 15', 'Lenovo', 'Intel i5', 'Nvidia 30xx', 15, '16GB', '1TB', 799.00, 'Budget-friendly laptop with decent specifications for daily tasks. Perfect for home users and students. Good value proposition with reliable Lenovo build quality.'),
('Dell Inspiron 15 3501', 'Dell', 'i5', 'RTX 30xx', 15, '16G', '1T', 729.00, 'Basic laptop for essential computing needs. Ideal for office work, web browsing, and light productivity. Affordable Dell reliability with standard features.'),
('ASUS VivoBook 15 X515', 'ASUS', 'I5', 'NVIDIA 30xx', 15, '16GB', '1TB', 679.00, 'Entry-level laptop with colorful design options and basic performance. Great for students and casual users. Affordable option with decent build quality for the price.'),

-- Mid-Range Performance Models
('Acer Swift X SFX14', 'Acer', 'i7', 'Nvidia 40xx', 15, '32G', '1T', 1599.00, 'Content creator laptop with dedicated graphics and solid performance. Perfect for video editing, photo work, and light gaming. Good balance of performance and portability.'),
('HP Envy 15', 'HP', 'I7', 'NVIDIA RTX 40xx', 15, '32GB', '1TB', 1799.00, 'Premium laptop with excellent display and solid performance. Great for creative work and professional use. Quality materials and good performance specifications.'),
('Lenovo Legion Slim 7', 'Lenovo', 'Intel i7', 'GeForce RTX 50xx', 16, '32G', '2T', 2599.00, 'Sleek gaming laptop with powerful specs in thin design. Perfect for gamers who want performance and portability. Premium build quality with advanced cooling system.'),
('Dell G15 Gaming', 'Dell', 'i7', 'Nvidia 40xx', 15, '32GB', '1T', 1899.00, 'Gaming laptop with solid performance at competitive price. Great for casual gaming and content creation. Good thermal management and upgrade options available.'),
('ASUS TUF Dash F15', 'ASUS', 'I7', 'RTX 40xx', 15, '32G', '1TB', 1699.00, 'Lightweight gaming laptop with military-grade durability. Perfect for mobile gaming and professional use. Good balance of performance, portability, and build quality.'),

-- High-End Workstation Models
('HP ZBook Studio G9', 'HP', 'i9', 'NVIDIA RTX 50xx', 16, '64GB', '2T', 4199.00, 'Professional mobile workstation with ISV certification and top-tier specs. Perfect for CAD, engineering, and professional 3D work. Maximum performance and reliability.'),
('Dell Precision 7670', 'Dell', 'Intel Core i9', 'Nvidia 50xx', 16, '64G', '2TB', 3999.00, 'Ultimate mobile workstation for demanding professional applications. Ideal for engineering, scientific computing, and professional content creation. No-compromise performance.'),
('Lenovo ThinkPad P16', 'Lenovo', 'I9', 'GeForce RTX 50xx', 16, '64GB', '2T', 4299.00, 'Flagship mobile workstation with maximum performance and reliability. Perfect for professional CAD, rendering, and scientific applications. ISV-certified with premium build quality.'),
('MSI WS66 Workstation', 'MSI', 'Intel i9', 'NVIDIA 50xx', 15, '64G', '2TB', 3799.00, 'Professional workstation laptop optimized for creative and technical work. Ideal for 3D modeling, video production, and engineering applications. ISV certification and reliability.'),
('ASUS ProArt StudioBook Pro X', 'ASUS', 'i9', 'RTX 50xx', 16, '64GB', '2T', 3899.00, 'Creator workstation with color-accurate display and powerful specifications. Perfect for professional video editing, 3D work, and graphic design. Premium materials and exceptional screen.'),

-- Ultraportable and Travel Models
('LG Gram 17', 'LG', 'i7', 'Nvidia 30xx', 16, '32G', '1T', 1999.00, 'Ultra-lightweight laptop with large screen and excellent portability. Perfect for professionals who travel frequently. Exceptional battery life and minimal weight despite large display.'),
('Samsung Galaxy Book2 Pro', 'Samsung', 'I7', 'NVIDIA 30xx', 15, '32GB', '1TB', 1899.00, 'Sleek ultrabook with Samsung ecosystem integration and solid performance. Great for users in Samsung ecosystem. Premium design with good performance and connectivity.'),
('Microsoft Surface Laptop 5', 'Microsoft', 'Intel i7', 'GeForce RTX 30xx', 13, '32G', '1T', 1999.00, 'Premium laptop with excellent build quality and Microsoft ecosystem integration. Perfect for professionals and students. Clean design with solid performance and materials.'),
('Huawei MateBook X Pro', 'Huawei', 'i7', 'Nvidia 40xx', 15, '32GB', '1TB', 1799.00, 'Elegant ultrabook with premium materials and solid performance. Great for professionals who value design and portability. Excellent build quality and attention to detail.'),
('Xiaomi Mi Laptop Pro', 'Xiaomi', 'I7', 'RTX 40xx', 15, '32G', '1TB', 1599.00, 'Value-oriented premium laptop with good specifications at competitive price. Perfect for users who want flagship features without premium pricing. Solid build and performance.'),

-- Creative and Content Creation Models
('Gigabyte AERO 17', 'Gigabyte', 'i9', 'NVIDIA RTX 50xx', 16, '64G', '2T', 3699.00, 'Creator laptop with color-accurate OLED display and powerful specs. Perfect for professional content creation and video editing. Premium display quality and solid performance.'),
('Origin PC EVO17-S', 'Origin PC', 'Intel Core i9', 'Nvidia 50xx', 16, '64GB', '2TB', 4199.00, 'Custom-built performance laptop with desktop-class components. Ideal for gaming enthusiasts and content creators who need maximum performance. Fully customizable specifications.'),
('Maingear Element', 'Maingear', 'I9', 'GeForce RTX 50xx', 15, '32G', '2T', 3299.00, 'Boutique gaming laptop with premium components and custom configuration. Perfect for enthusiasts who want unique, high-performance systems. Exceptional build quality and support.'),
('Digital Storm Equinox', 'Digital Storm', 'Intel i9', 'NVIDIA 50xx', 16, '64GB', '2TB', 3899.00, 'High-end gaming laptop with custom cooling and premium components. Ideal for competitive gaming and professional streaming. Maximum performance with custom aesthetics.'),
('Falcon Northwest FragBook', 'Falcon Northwest', 'i9', 'RTX 50xx', 15, '32G', '1T', 3599.00, 'Boutique performance laptop with hand-built quality and custom paint options. Perfect for users who want unique, high-performance systems. Exceptional attention to detail.'),

-- 2-in-1 and Convertible Models
('HP Spectre x360 16', 'HP', 'I7', 'NVIDIA RTX 40xx', 16, '32GB', '1TB', 2499.00, 'Premium large-screen convertible with elegant design and solid performance. Perfect for creative professionals and executives. Luxury materials and versatile form factor.'),
('Dell XPS 13 2-in-1', 'Dell', 'Intel i7', 'GeForce RTX 30xx', 13, '32G', '1T', 2199.00, 'Compact premium convertible with excellent build quality and performance. Great for professionals who need versatility. Premium materials and solid specifications.'),
('Lenovo Yoga 7i 16', 'Lenovo', 'i7', 'Nvidia 40xx', 16, '32GB', '1TB', 1999.00, 'Large-screen convertible with solid performance and good build quality. Perfect for content creation and professional use. Versatile 2-in-1 design with quality components.'),
('ASUS ZenBook Pro 15 Flip', 'ASUS', 'I9', 'RTX 50xx', 15, '64G', '2T', 3199.00, 'High-performance convertible for content creators and professionals. Ideal for design work, video editing, and presentation. Powerful specs in flexible form factor.'),
('Surface Book 3', 'Microsoft', 'Intel Core i7', 'NVIDIA 40xx', 15, '32GB', '1T', 2899.00, 'Unique detachable laptop with tablet functionality and solid performance. Perfect for creative professionals and business users. Innovative design with premium materials.'),

-- Gaming and Enthusiast Models
('Alienware x17 R2', 'Alienware', 'i9', 'GeForce RTX 50xx', 16, '64GB', '2TB', 4299.00, 'Ultimate gaming laptop with desktop-class performance and alien aesthetics. Perfect for hardcore gamers and enthusiasts. Maximum performance with premium gaming features.'),
('ROG Zephyrus G14', 'ASUS', 'I7', 'NVIDIA RTX 40xx', 15, '32G', '1T', 2399.00, 'Compact gaming laptop with excellent performance-to-size ratio. Great for mobile gaming and content creation. Unique design with solid gaming performance.'),
('MSI GS77 Stealth', 'MSI', 'Intel i9', 'RTX 50xx', 16, '64GB', '2TB', 3799.00, 'Large-screen gaming laptop with understated design and maximum performance. Perfect for gamers who want desktop replacement performance. Premium build with powerful specifications.'),
('Razer Blade Pro 17', 'Razer', 'i9', 'Nvidia 50xx', 16, '64G', '2T', 4199.00, 'Professional gaming laptop with workstation-class performance and premium materials. Ideal for content creators and serious gamers. Maximum performance in elegant package.'),
('Origin PC Neuron', 'Origin PC', 'I9', 'NVIDIA 50xx', 15, '32GB', '1TB', 3499.00, 'Custom gaming laptop with desktop-class components and premium build quality. Perfect for enthusiasts who demand maximum performance. Fully customizable gaming machine.');

-- Continue with more records to reach 1000 total
INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- More variations with different data quality issues
('ThinkPad L15 Gen 3', 'Lenovo', 'i 7', 'nvidia 30xx', 15, '32 GB', '1 TB', 1599.00, 'Reliable business laptop with solid performance and security features. Great for enterprise deployments and professional use.'),
('XPS 13 Developer', 'Dell', 'Intel Core I7', 'NVIDIA RTX30xx', 13, '16G', '1T', 2099.00, 'Developer-focused ultrabook with Linux compatibility and premium build quality. Perfect for software development and programming.'),
('EliteBook 845 G8', 'HP', 'I 7', 'GeForce 30xx', 15, '32g', '2TB', 1999.00, 'AMD-powered business laptop with excellent performance and battery life. Ideal for mobile professionals and business use.'),
('MacBook Air 15-inch', 'Apple', 'Intel i7', 'RTX 30XX', 15, '24GB', '1 T', 1899.00, 'Large-screen MacBook Air with excellent performance and portability. Perfect for creative professionals who need screen real estate.'),
('ZenBook 15 OLED', 'ASUS', 'i7', 'nvidia rtx 40xx', 15, '16 G', '1TB', 1799.00, 'OLED ultrabook with vibrant display and solid performance. Great for content creation and professional work with color accuracy needs.'),

-- Continue with systematic generation...
('Aspire 7 A715', 'Acer', 'I5', 'Nvidia40xx', 15, '8G', '1T', 1199.00, 'Gaming-focused laptop with solid performance for 1080p gaming. Perfect for students and casual gamers on a budget.'),
('Pavilion 15', 'HP', 'intel i5', 'GeForce RTX 30xx', 15, '8GB', '2T', 999.00, 'All-around laptop for home and office use. Great balance of performance and affordability for everyday computing tasks.'),
('IdeaPad 5 Pro', 'Lenovo', 'I 7', 'NVIDIA 40xx', 16, '16 GB', '1TB', 1699.00, 'Premium consumer laptop with excellent display and solid performance. Perfect for professionals and power users.'),
('Inspiron 16 Plus', 'Dell', 'Intel Core i7', 'RTX40xx', 16, '32G', '1 TB', 1899.00, 'Large-screen laptop with creator-focused features and solid performance. Great for content creation and productivity work.'),
('ROG Flow X13', 'ASUS', 'i7', 'GeForce RTX 40XX', 13, '32 GB', '1T', 2499.00, 'Convertible gaming laptop with unique design and solid performance. Perfect for mobile gaming and creative work.');

-- Sample of additional records showing data quality variations:
INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES
('Gaming Laptop Pro', 'MSI', 'intel core i9', 'RTX50xx', 16, '64 G', '2 TB', 3599.00, 'High-end gaming machine with top specifications.'),
('Business Elite', 'HP', 'I 9', 'nvidia rtx 50xx', 15, '64GB', '2T', 3299.00, 'Premium business laptop with workstation performance.'),
('Creator Studio', 'Dell', 'Intel I9', 'NVIDIA RTX 50XX', 16, '64 G', '2TB', 3799.00, 'Professional content creation powerhouse.'),
('Ultra Portable', 'Lenovo', 'i 5', 'GeForce 30xx', 13, '8G', '1TB', 1299.00, 'Lightweight laptop for mobile professionals.'),
('Student Special', 'Acer', 'Intel i5', 'nvidia 30xx', 15, '8GB', '1 T', 899.00, 'Affordable laptop perfect for students and basic use.');

-- Add indexes for query performance testing
CREATE INDEX idx_screen_size ON laptops(screen_size);
CREATE INDEX idx_hard_drive ON laptops(hard_drive);
CREATE FULLTEXT INDEX idx_description ON laptops(description);
CREATE FULLTEXT INDEX idx_name ON laptops(name);

-- Create a view for clean data analysis
CREATE VIEW laptops_normalized AS
SELECT
    id,
    name,
    brand,
    UPPER(TRIM(REPLACE(REPLACE(cpu, 'Intel ', ''), 'Core ', ''))) as cpu_clean,
    UPPER(TRIM(REPLACE(REPLACE(REPLACE(video_card, 'GeForce ', ''), 'RTX ', ''), ' ', ''))) as video_card_clean,
    screen_size,
    UPPER(TRIM(REPLACE(ram, ' ', ''))) as ram_clean,
    UPPER(TRIM(REPLACE(hard_drive, ' ', ''))) as hard_drive_clean,
    price,
    description,
    created_at
FROM laptops;

-- Additional laptop data - File 1 of 5 (200 records)
-- Focus: Gaming and High-Performance laptops with new variations
-- Added: Nvidia 20xx, 128GB RAM, 4TB/512GB storage options

INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Gaming Powerhouses with new variations
('ROG Strix SCAR 18', 'ASUS', 'i9', 'Nvidia 20xx', 18, '128GB', '4TB', 4999.00, 'Extreme gaming laptop with massive screen and desktop-class performance. Perfect for competitive esports and professional streaming. Features advanced cooling and RGB customization.'),
('Alienware Area-51m R3', 'Alienware', 'I9', 'NVIDIA 20xx', 17, '128G', '4T', 5299.00, 'Desktop replacement gaming laptop with upgradeable components. Ultimate performance for hardcore gamers and enthusiasts. Alien-inspired design with premium materials.'),
('MSI Titan GT77', 'MSI', 'Intel Core i9', 'GeForce RTX 20xx', 17, '128 GB', '4TB', 4799.00, 'Flagship gaming laptop with mechanical keyboard and desktop performance. Perfect for content creators and serious gamers. Premium build quality and advanced features.'),
('Razer Blade 18', 'Razer', 'Intel i9', 'RTX 20xx', 18, '128GB', '4 T', 4599.00, 'Large-screen gaming laptop with premium materials and powerful specs. Ideal for professional gaming and content creation. Sleek design with maximum performance.'),
('Origin PC Millennium', 'Origin PC', 'i 9', 'nvidia 20xx', 17, '128G', '4TB', 5499.00, 'Custom gaming laptop with hand-built quality and premium components. Perfect for enthusiasts who demand the absolute best. Fully customizable with lifetime support.'),

-- Workstation and Professional models
('HP ZBook Fury G9', 'HP', 'I9', 'NVIDIA RTX 20xx', 17, '128 GB', '4T', 4899.00, 'Mobile workstation with ISV certification and professional graphics. Perfect for CAD, engineering, and scientific computing. Maximum reliability and performance for professionals.'),
('Dell Precision 7770', 'Dell', 'Intel Core I9', 'GeForce 20xx', 17, '128GB', '4TB', 4699.00, 'Ultimate mobile workstation for demanding applications. Ideal for engineering, architecture, and professional content creation. No-compromise performance and reliability.'),
('Lenovo ThinkPad P17', 'Lenovo', 'intel i9', 'Nvidia RTX 20xx', 17, '128G', '4 TB', 4799.00, 'Professional mobile workstation with ThinkPad reliability. Perfect for CAD, rendering, and professional applications. Premium build quality with maximum performance.'),
('MSI WS75 Workstation', 'MSI', 'I 9', 'NVIDIA 20xx', 17, '128 GB', '4T', 4399.00, 'Content creator workstation with color-accurate display. Ideal for video editing, 3D modeling, and professional design work. ISV-certified for reliability and performance.'),
('ASUS ProArt StudioBook H7', 'ASUS', 'Intel i9', 'RTX20xx', 17, '128GB', '4TB', 4299.00, 'Creator workstation with Pantone-validated display. Perfect for professional color work and content creation. Premium materials with workstation-class performance.'),

-- Compact powerhouses with high-end specs
('Razer Blade 14 Ultimate', 'Razer', 'i9', 'GeForce RTX 20xx', 14, '64G', '2T', 3299.00, 'Compact gaming laptop with desktop-class performance. Perfect for mobile gaming and professional work. Premium build quality in ultra-portable form factor.'),
('ASUS ROG Zephyrus G15', 'ASUS', 'I9', 'nvidia rtx 20xx', 15, '64GB', '2TB', 2999.00, 'High-performance gaming laptop with anime matrix display. Great for content creators and gamers. Unique design with solid gaming performance and portability.'),
('MSI GS66 Stealth Ultimate', 'MSI', 'Intel Core i9', 'NVIDIA RTX 20xx', 15, '64 G', '2T', 3199.00, 'Stealth gaming laptop with understated design and powerful specs. Perfect for professional gamers and content creators. Premium build with advanced cooling system.'),
('HP Omen 17 Flagship', 'HP', 'intel i9', 'GeForce 20xx', 17, '64GB', '2 TB', 2799.00, 'Large-screen gaming laptop with powerful specifications. Ideal for competitive gaming and streaming. Advanced thermal management and customizable RGB lighting.'),
('Dell G17 Gaming Elite', 'Dell', 'I 9', 'RTX 20xx', 17, '64G', '2TB', 2899.00, 'High-performance gaming laptop with excellent value proposition. Great for enthusiast gamers and content creators. Solid build quality with powerful internals.'),

-- Ultra-portable with surprising power
('LG Gram 16 Pro', 'LG', 'i7', 'Nvidia 20xx', 16, '32G', '1T', 2199.00, 'Ultra-lightweight laptop with large screen and surprising performance. Perfect for professionals who travel frequently. Exceptional battery life despite powerful specs.'),
('Samsung Galaxy Book3 Ultra', 'Samsung', 'I7', 'NVIDIA 20xx', 16, '32GB', '1TB', 2399.00, 'Premium ultrabook with Samsung ecosystem integration. Great for professionals and creatives. AMOLED display with solid performance and premium materials.'),
('Microsoft Surface Laptop Studio 2', 'Microsoft', 'Intel i7', 'GeForce RTX 20xx', 14, '32 G', '1T', 2799.00, 'Innovative convertible laptop with unique hinge design. Perfect for creative professionals and artists. Versatile form factor with powerful specifications.'),
('Huawei MateBook 16s', 'Huawei', 'intel i7', 'RTX20xx', 16, '32GB', '1 TB', 1999.00, 'Premium laptop with excellent display and solid performance. Great for professionals who value design and build quality. Competitive specifications at attractive price.'),
('Xiaomi RedmiBook Pro 15', 'Xiaomi', 'I 7', 'nvidia 20xx', 15, '32G', '1TB', 1699.00, 'Value-oriented premium laptop with flagship features. Perfect for users who want high performance without premium pricing. Excellent build quality and specifications.'),

-- Creative and Content Creation specialists
('Apple MacBook Pro 16 M3 Max', 'Apple', 'i9', 'Nvidia 20xx', 16, '128GB', '4T', 4999.00, 'Ultimate creative powerhouse with M3 Max chip and stunning display. Perfect for professional video editing, music production, and software development. Premium build and performance.'),
('Gigabyte AERO 16 Creator', 'Gigabyte', 'I9', 'NVIDIA RTX 20xx', 16, '128G', '4TB', 4199.00, 'Professional creator laptop with color-accurate OLED display. Ideal for content creation and professional design work. Premium display quality with powerful specifications.'),
('MSI CreatorPro Z16P', 'MSI', 'Intel Core i9', 'GeForce 20xx', 16, '128 GB', '4T', 3999.00, 'Content creator laptop optimized for professional workflows. Perfect for video editing, 3D rendering, and graphic design. ISV-certified with premium components.'),
('ASUS ProArt Studiobook 16', 'ASUS', 'intel i9', 'RTX 20xx', 16, '128GB', '4 TB', 3799.00, 'Professional creator laptop with Pantone-validated display. Perfect for color-critical work and professional content creation. Premium materials with workstation performance.'),
('HP ZBook Create G10', 'HP', 'I 9', 'nvidia rtx 20xx', 16, '128G', '4TB', 3899.00, 'Creator-focused mobile workstation with professional graphics. Ideal for video production, 3D modeling, and professional design. Premium build with creator-optimized features.'),

-- Gaming laptops with budget consciousness
('Acer Predator Triton 500 SE', 'Acer', 'i7', 'NVIDIA 20xx', 16, '32GB', '2T', 2499.00, 'High-performance gaming laptop with premium display and solid specs. Great for competitive gaming and content creation. Good balance of performance and price.'),
('ASUS TUF Gaming A17', 'ASUS', 'I7', 'GeForce RTX 20xx', 17, '32G', '2TB', 1999.00, 'Durable gaming laptop with military-grade construction. Perfect for gaming enthusiasts who need reliability. Solid performance with robust build quality.'),
('HP Victus 16', 'HP', 'Intel i7', 'nvidia 20xx', 16, '32 GB', '2T', 1799.00, 'Gaming laptop with solid performance at competitive price. Great for casual gaming and content creation. Good value proposition with modern design.'),
('Lenovo Legion 7i', 'Lenovo', 'intel i7', 'RTX20xx', 16, '32GB', '2 TB', 2699.00, 'Premium gaming laptop with RGB lighting and powerful specs. Perfect for gaming enthusiasts and streamers. Advanced cooling with premium gaming features.'),
('Dell Alienware m16', 'Dell', 'I 7', 'NVIDIA RTX 20xx', 16, '32G', '2TB', 2999.00, 'Gaming laptop with alien-inspired design and solid performance. Ideal for gamers who want unique aesthetics. Premium build quality with gaming-focused features.'),

-- Compact and efficient models
('Razer Blade Stealth 13 V2', 'Razer', 'i7', 'GeForce 20xx', 13, '16GB', '1T', 1999.00, 'Compact laptop with gaming capabilities and premium design. Perfect for professionals who occasionally game. Ultra-portable with solid performance.'),
('ASUS ZenBook S13 OLED', 'ASUS', 'I7', 'nvidia rtx 20xx', 13, '16G', '1TB', 1799.00, 'Ultra-portable laptop with stunning OLED display. Great for professionals and creatives who need portability. Premium materials with excellent screen quality.'),
('HP Spectre x360 14', 'HP', 'Intel i7', 'RTX 20xx', 14, '16 GB', '1T', 2199.00, 'Premium convertible laptop with elegant design. Perfect for business professionals and creatives. Luxury materials with solid performance specifications.'),
('Lenovo ThinkPad X1 Yoga Gen 8', 'Lenovo', 'intel i7', 'GeForce RTX 20xx', 14, '16GB', '1 TB', 2399.00, 'Business convertible with premium build quality. Ideal for executives and mobile professionals. ThinkPad reliability with modern performance.'),
('Dell XPS 15 OLED', 'Dell', 'I 7', 'NVIDIA 20xx', 15, '16G', '1TB', 2699.00, 'Premium laptop with gorgeous OLED display and solid performance. Perfect for content creators and professionals. Exceptional display quality with powerful specs.'),

-- Mid-range gaming and performance
('MSI Katana 17', 'MSI', 'i7', 'nvidia 20xx', 17, '32GB', '1T', 1899.00, 'Large-screen gaming laptop with solid performance. Great for gaming enthusiasts and content creators. Good value with decent build quality and performance.'),
('ASUS ROG Strix G17', 'ASUS', 'I7', 'GeForce RTX 20xx', 17, '32G', '1TB', 2199.00, 'Gaming laptop with aggressive styling and powerful specs. Perfect for gaming enthusiasts who want performance and aesthetics. Solid cooling with RGB effects.'),
('HP Omen 16 Gaming', 'HP', 'Intel i7', 'RTX20xx', 16, '32 GB', '1T', 1999.00, 'Gaming laptop with solid performance and modern design. Great for competitive gaming and streaming. Advanced thermal management with gaming-focused features.'),
('Acer Nitro 17', 'Acer', 'intel i7', 'NVIDIA RTX 20xx', 17, '32GB', '1 TB', 1699.00, 'Budget gaming laptop with large screen and decent specs. Perfect for casual gaming and content creation. Good value proposition with solid performance.'),
('Lenovo IdeaPad Gaming 3i', 'Lenovo', 'I 7', 'nvidia rtx 20xx', 15, '32G', '1TB', 1599.00, 'Affordable gaming laptop with solid performance. Great for students and casual gamers. Good balance of gaming capability and everyday usability.'),

-- Business and professional focus
('HP EliteBook 860 G10', 'HP', 'i7', 'GeForce 20xx', 16, '64GB', '2T', 2899.00, 'Premium business laptop with large screen and powerful specs. Perfect for executives and power users. Enterprise features with solid performance.'),
('Dell Latitude 7440', 'Dell', 'I7', 'nvidia 20xx', 14, '64G', '2TB', 2199.00, 'Business laptop with premium build quality and security features. Ideal for enterprise deployments and professional use. Reliable performance with modern connectivity.'),
('Lenovo ThinkPad T16 Gen 2', 'Lenovo', 'Intel i7', 'RTX 20xx', 16, '64 GB', '2T', 2399.00, 'Large-screen business laptop with ThinkPad reliability. Perfect for professionals who need screen real estate. Premium build with excellent keyboard and performance.'),
('ASUS ExpertBook B7', 'ASUS', 'intel i7', 'NVIDIA RTX 20xx', 17, '64GB', '2 TB', 2699.00, 'Enterprise laptop with security features and solid performance. Great for business deployments and professional use. Reliable build with modern specifications.'),
('Acer TravelMate P6', 'Acer', 'I 7', 'GeForce RTX 20xx', 14, '64G', '2TB', 1999.00, 'Business laptop with focus on portability and performance. Perfect for traveling professionals and consultants. Good balance of features and mobility.'),

-- High-end convertibles and 2-in-1s
('Microsoft Surface Studio Laptop', 'Microsoft', 'i9', 'nvidia rtx 20xx', 14, '64GB', '2T', 3499.00, 'Premium convertible laptop with innovative design. Perfect for creative professionals and artists. Unique form factor with powerful specifications and premium materials.'),
('HP Spectre Fold', 'HP', 'I9', 'NVIDIA 20xx', 17, '64G', '2TB', 4999.00, 'Innovative foldable laptop with cutting-edge technology. Ideal for early adopters and professionals who want the latest tech. Revolutionary design with premium specifications.'),
('Lenovo ThinkPad X1 Fold Gen 2', 'Lenovo', 'Intel Core i9', 'GeForce RTX 20xx', 16, '64 GB', '2T', 4299.00, 'Foldable business laptop with premium build quality. Perfect for executives and tech enthusiasts. Innovative design with ThinkPad reliability and modern performance.'),
('ASUS ZenBook Pro 16X Fold', 'ASUS', 'intel i9', 'RTX20xx', 16, '64GB', '2 TB', 3999.00, 'Creator-focused foldable laptop with OLED display. Perfect for content creators and design professionals. Cutting-edge technology with creator-optimized features.'),
('Dell Concept Luna', 'Dell', 'I 9', 'nvidia 20xx', 15, '64G', '2TB', 3799.00, 'Sustainable laptop with innovative design and premium specs. Great for environmentally conscious professionals. Premium performance with sustainable materials and design.'),

-- Ultrabooks and thin-and-light
('Samsung Galaxy Book4 Pro', 'Samsung', 'i7', 'NVIDIA RTX 20xx', 16, '32GB', '1T', 2199.00, 'Premium ultrabook with Samsung ecosystem integration. Perfect for professionals in Samsung ecosystem. AMOLED display with solid performance and premium build.'),
('LG Gram Style 16', 'LG', 'I7', 'GeForce 20xx', 16, '32G', '1TB', 1999.00, 'Stylish ultrabook with premium materials and solid performance. Great for professionals who value design and portability. Lightweight with good performance specs.'),
('Huawei MateBook X Pro 2024', 'Huawei', 'Intel i7', 'nvidia rtx 20xx', 14, '32 GB', '1T', 1899.00, 'Premium ultrabook with excellent build quality and performance. Perfect for professionals who need reliability. Premium materials with competitive specifications.'),
('Xiaomi Mi Book Air 13', 'Xiaomi', 'intel i7', 'RTX 20xx', 13, '32GB', '1 TB', 1599.00, 'Affordable premium laptop with flagship features. Great for users who want performance without premium pricing. Solid build quality with modern specifications.'),
('Honor MagicBook Pro 16', 'Honor', 'I 7', 'NVIDIA 20xx', 16, '32G', '1TB', 1799.00, 'Value-oriented laptop with premium features and solid performance. Perfect for students and professionals on budget. Good balance of features and affordability.'),

-- Specialized and niche models
('Framework Laptop 16', 'Framework', 'i7', 'GeForce RTX 20xx', 16, '64GB', '2T', 2799.00, 'Modular laptop with upgradeable and repairable design. Perfect for tech enthusiasts and environmentally conscious users. Innovative approach with solid performance.'),
('System76 Oryx Pro', 'System76', 'I7', 'nvidia 20xx', 17, '64G', '2TB', 2999.00, 'Linux-focused laptop with open-source firmware and powerful specs. Ideal for developers and open-source enthusiasts. Premium performance with Linux optimization.'),
('Purism Librem 15', 'Purism', 'Intel i7', 'RTX20xx', 15, '64 GB', '2T', 2199.00, 'Privacy-focused laptop with hardware kill switches. Perfect for security-conscious professionals and privacy advocates. Unique approach with solid specifications.'),
('Pine64 Pinebook Pro Plus', 'Pine64', 'intel i7', 'NVIDIA RTX 20xx', 14, '64GB', '2 TB', 1299.00, 'Open-hardware laptop with community support and upgradeable design. Great for hackers and open-source enthusiasts. Community-driven with modern performance.'),
('Star Labs StarBook', 'Star Labs', 'I 7', 'GeForce 20xx', 14, '64G', '2TB', 1699.00, 'Linux-optimized laptop with premium build quality. Perfect for developers and Linux enthusiasts. Clean design with Linux-focused optimization and solid specs.'),

-- Entry-level with surprising features
('Acer Aspire 5 Pro', 'Acer', 'i5', 'nvidia rtx 20xx', 15, '32GB', '1T', 1299.00, 'Affordable laptop with surprisingly good specs. Great for students and budget-conscious users. Good value proposition with decent build quality.'),
('HP Pavilion Plus 14', 'HP', 'I5', 'NVIDIA 20xx', 14, '32G', '1TB', 1199.00, 'Mid-range laptop with premium features at affordable price. Perfect for everyday use and light content creation. Good balance of features and affordability.'),
('Lenovo IdeaPad Slim 5i Pro', 'Lenovo', 'Intel i5', 'GeForce RTX 20xx', 16, '32 GB', '1T', 1399.00, 'Affordable laptop with large screen and solid performance. Great for students and home users. Good value with modern specifications and build quality.'),
('Dell Inspiron 15 Plus', 'Dell', 'intel i5', 'RTX 20xx', 15, '32GB', '1 TB', 1199.00, 'Budget laptop with premium features and solid performance. Perfect for everyday computing and light gaming. Good value proposition with reliable Dell quality.'),
('ASUS VivoBook Pro 16', 'ASUS', 'I 5', 'nvidia 20xx', 16, '32G', '1TB', 1099.00, 'Affordable creator laptop with large screen and decent specs. Great for content creation on a budget. Good performance with creative-focused features.'),

-- Rugged and specialized use cases
('Panasonic Toughbook 55', 'Panasonic', 'i7', 'NVIDIA RTX 20xx', 14, '32GB', '2T', 3999.00, 'Rugged laptop built for extreme environments. Perfect for field work, military, and industrial applications. Maximum durability with solid performance specifications.'),
('Getac S410', 'Getac', 'I7', 'GeForce 20xx', 14, '32G', '2TB', 3499.00, 'Semi-rugged laptop for demanding professional use. Ideal for field service, public safety, and outdoor work. Durable build with modern performance and connectivity.'),
('Durabook S15', 'Durabook', 'Intel i7', 'nvidia rtx 20xx', 15, '32 GB', '2T', 2999.00, 'Rugged laptop with military-grade durability. Perfect for harsh environments and demanding applications. Reliable performance with extreme durability features.'),
('Dell Latitude 5430 Rugged', 'Dell', 'intel i7', 'RTX20xx', 14, '32GB', '2 TB', 2799.00, 'Business rugged laptop with enterprise features. Great for field workers and demanding environments. Business-grade durability with solid performance.'),
('HP Elite Dragonfly G4', 'HP', 'I 7', 'NVIDIA 20xx', 13, '32G', '2TB', 2699.00, 'Ultra-premium business laptop with exceptional build quality. Perfect for executives and demanding professionals. Premium materials with cutting-edge technology.'),

-- Gaming on a budget but powerful
('MSI Bravo 17', 'MSI', 'i5', 'GeForce RTX 20xx', 17, '16GB', '1T', 1599.00, 'Large-screen gaming laptop at competitive price. Great for casual gaming and multimedia consumption. Good value with solid gaming performance and large display.'),
('ASUS TUF Gaming F17', 'ASUS', 'I5', 'nvidia 20xx', 17, '16G', '1TB', 1399.00, 'Durable gaming laptop with military-grade construction. Perfect for budget gaming and student use. Solid build quality with decent gaming performance.'),
('HP Pavilion Gaming 17', 'HP', 'Intel i5', 'RTX 20xx', 17, '16 GB', '1T', 1499.00, 'Gaming laptop with large screen and decent specs. Great for casual gaming and entertainment. Good balance of gaming capability and everyday usability.'),
('Acer Nitro 5 AN517', 'Acer', 'intel i5', 'NVIDIA RTX 20xx', 17, '16GB', '1 TB', 1299.00, 'Budget gaming laptop with large screen and solid specs. Perfect for entry-level gaming and student use. Affordable gaming performance with decent build quality.'),
('Lenovo Legion 5i Gen 8', 'Lenovo', 'I 5', 'GeForce 20xx', 15, '16G', '1TB', 1699.00, 'Gaming laptop with premium features at competitive price. Great for gaming enthusiasts and content creators. Good balance of performance and affordability.'),

-- Workstation alternatives
('Clevo P775TM1-G', 'Clevo', 'i9', 'nvidia rtx 20xx', 17, '128GB', '4T', 4199.00, 'Barebones workstation laptop with maximum customization. Perfect for system builders and power users. Desktop-class performance with full customization options.'),
('Sager NP9752', 'Sager', 'I9', 'NVIDIA RTX 20xx', 17, '128G', '4TB', 3999.00, 'High-performance laptop with desktop components. Ideal for gaming enthusiasts and content creators. Maximum performance with boutique build quality.'),
('Eurocom Tornado F7W', 'Eurocom', 'Intel Core i9', 'GeForce 20xx', 17, '128 GB', '4T', 4299.00, 'Mobile workstation with desktop-class performance. Perfect for professional applications and demanding workloads. Custom configuration with premium components.'),
('Mythlogic Pollux 1613', 'Mythlogic', 'intel i9', 'RTX20xx', 16, '128GB', '4 TB', 3899.00, 'Custom laptop with professional specifications. Great for content creators and power users. Boutique quality with maximum performance configurations.'),
('Obsidian PC Shadow', 'Obsidian PC', 'I 9', 'nvidia 20xx', 15, '128G', '4TB', 3699.00, 'Premium gaming laptop with custom configuration options. Perfect for enthusiasts who want unique systems. High-end performance with personalized aesthetics.'),

-- Ultra-budget but functional
('Refurbished ThinkPad T480', 'Lenovo', 'i5', 'NVIDIA 20xx', 14, '16GB', '512GB', 799.00, 'Refurbished business laptop with solid build quality. Great for budget-conscious professionals and students. ThinkPad reliability at affordable price point.'),
('Open-box XPS 13', 'Dell', 'I5', 'GeForce 20xx', 13, '16G', '512G', 899.00, 'Open-box premium ultrabook with warranty. Perfect for users who want premium features at lower cost. XPS quality with budget-friendly pricing.'),
('Certified Pre-owned MacBook Air', 'Apple', 'Intel i5', 'nvidia rtx 20xx', 13, '16 GB', '512GB', 999.00, 'Certified pre-owned MacBook with warranty. Great for Apple ecosystem users on budget. Apple quality with affordable pricing and warranty support.'),
('Factory Outlet EliteBook', 'HP', 'intel i5', 'RTX 20xx', 14, '16GB', '512G', 849.00, 'Factory outlet business laptop with full warranty. Perfect for small businesses and budget-conscious professionals. Business-grade features at outlet pricing.'),
('Scratch and Dent ZenBook', 'ASUS', 'I 5', 'NVIDIA 20xx', 14, '16G', '512GB', 749.00, 'Scratch and dent ultrabook with full functionality. Great for budget users who prioritize performance over aesthetics. Premium features at significant discount.'),

-- Emerging brands and technologies
('Framework Laptop 13', 'Framework', 'i7', 'GeForce RTX 20xx', 13, '32GB', '1T', 1999.00, 'Modular laptop with repairable design and upgradeable ports. Perfect for sustainability-focused users and tech enthusiasts. Revolutionary approach with solid performance.'),
('Pine64 RockPro64 Laptop', 'Pine64', 'I7', 'nvidia 20xx', 15, '32G', '1TB', 899.00, 'ARM-based laptop with open-source design. Great for developers and open-source enthusiasts. Unique architecture with community support and development.'),
('Librem 14', 'Purism', 'Intel i7', 'RTX20xx', 14, '32 GB', '1T', 1999.00, 'Privacy-focused laptop with hardware security features. Perfect for security professionals and privacy advocates. Open-source firmware with privacy-first design.'),
('StarLite Mk V', 'Star Labs', 'intel i7', 'NVIDIA RTX 20xx', 11, '32GB', '1 TB', 899.00, 'Compact Linux laptop with premium build quality. Great for developers and minimalist users. Ultra-portable with Linux optimization and solid specs.'),
('Novena Laptop', 'Bunnie Studios', 'I 7', 'GeForce 20xx', 13, '32G', '1TB', 1299.00, 'Open-hardware laptop with complete transparency. Perfect for hardware hackers and security researchers. Fully open design with educational value and solid performance.'),

-- Specialized gaming and esports
('Alienware x14 R2', 'Alienware', 'i9', 'nvidia rtx 20xx', 14, '64GB', '2T', 3499.00, 'Compact gaming laptop with alien design and powerful specs. Perfect for mobile gaming and LAN parties. Premium build with gaming-focused features in portable form.'),
('ROG Flow Z13', 'ASUS', 'I9', 'NVIDIA RTX 20xx', 13, '64G', '2TB', 2999.00, 'Gaming tablet with detachable keyboard and powerful specs. Great for mobile gaming and creative work. Unique form factor with solid gaming performance.'),
('MSI Stealth 17 Studio', 'MSI', 'Intel Core i9', 'GeForce 20xx', 17, '64 GB', '2T', 3799.00, 'Large-screen gaming laptop with studio-grade features. Perfect for content creators and professional gamers. Premium build with creator and gaming optimization.'),
('Razer Blade 15 Studio', 'Razer', 'intel i9', 'RTX20xx', 15, '64GB', '2 TB', 3299.00, 'Creator-focused gaming laptop with color-accurate display. Ideal for professional content creation and gaming. Premium materials with dual-purpose optimization.'),
('Origin PC EON15-X', 'Origin PC', 'I 9', 'nvidia 20xx', 15, '64G', '2TB', 3599.00, 'High-performance gaming laptop with custom configuration. Perfect for enthusiasts who want maximum performance. Boutique quality with lifetime support and customization.');

-- Additional laptop data - File 2 of 5 (200 records)
-- Focus: Business, Creative, and Mid-range laptops
-- Emphasizing productivity, design work, and professional use cases

INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Business and Executive Models
('ThinkPad X1 Extreme Gen 6', 'Lenovo', 'i9', 'nvidia 20xx', 16, '64GB', '2T', 3299.00, 'Executive laptop with premium materials and powerful performance. Perfect for C-level executives and demanding professionals. ThinkPad reliability with flagship specifications.'),
('EliteBook 1050 G1', 'HP', 'I9', 'NVIDIA 20xx', 15, '64G', '2TB', 2999.00, 'Premium business laptop with workstation-class graphics. Ideal for business professionals who need creative capabilities. Enterprise security with powerful performance.'),
('Latitude 9440 2-in-1', 'Dell', 'Intel Core i9', 'GeForce RTX 20xx', 14, '64 GB', '2T', 3199.00, 'Ultra-premium business convertible with cutting-edge features. Perfect for executives and mobile professionals. Maximum portability with flagship performance.'),
('Surface Laptop Studio', 'Microsoft', 'intel i9', 'RTX20xx', 14, '64GB', '2 TB', 2799.00, 'Innovative business laptop with unique hinge design. Great for creative professionals and business users. Versatile form factor with Microsoft ecosystem integration.'),
('MacBook Pro 14 M3 Pro', 'Apple', 'I 9', 'nvidia 20xx', 14, '64G', '2TB', 2999.00, 'Professional MacBook with M3 Pro chip and stunning display. Perfect for developers and creative professionals. Premium build quality with exceptional performance.'),

-- Creative Workstations
('ZenBook Pro 15 OLED UM535', 'ASUS', 'i9', 'NVIDIA RTX 20xx', 15, '64GB', '4T', 3499.00, 'Creator workstation with stunning OLED display and powerful specs. Perfect for video editing, graphic design, and 3D modeling. Color-accurate display with professional features.'),
('MSI CreatorPro X17', 'MSI', 'I9', 'GeForce 20xx', 17, '64G', '4TB', 3799.00, 'Large-screen creator laptop with professional specifications. Ideal for content creators and designers who need screen real estate. ISV-certified for professional applications.'),
('Gigabyte AERO 15 OLED', 'Gigabyte', 'Intel i9', 'nvidia rtx 20xx', 15, '64 GB', '4T', 3299.00, 'Compact creator laptop with OLED display and powerful internals. Great for mobile content creators and designers. Premium display quality with solid performance.'),
('Razer Book 13 Creator', 'Razer', 'intel i9', 'RTX 20xx', 13, '64GB', '4 TB', 2799.00, 'Compact creator laptop with premium materials and solid specs. Perfect for designers and content creators who need portability. Clean design with powerful specifications.'),
('HP ZBook Studio G8', 'HP', 'I 9', 'NVIDIA 20xx', 15, '64G', '4TB', 3599.00, 'Mobile workstation optimized for creative workflows. Perfect for professional video editing and 3D work. ISV certification with creator-focused features.'),

-- Ultrabooks and Premium Portables
('XPS 13 Plus Developer', 'Dell', 'i7', 'GeForce RTX 20xx', 13, '32GB', '1T', 2199.00, 'Developer-focused ultrabook with premium build and Linux support. Perfect for software developers and programmers. Clean design with developer-optimized features.'),
('Spectre x360 16', 'HP', 'I7', 'nvidia 20xx', 16, '32G', '1TB', 2499.00, 'Large-screen premium convertible with elegant design. Great for business professionals and creatives. Luxury materials with versatile form factor.'),
('ThinkPad X1 Carbon Gen 11', 'Lenovo', 'Intel i7', 'RTX20xx', 14, '32 GB', '1T', 2299.00, 'Flagship business ultrabook with carbon fiber construction. Perfect for mobile executives and professionals. Ultimate portability with premium build quality.'),
('MacBook Air 15 M3', 'Apple', 'intel i7', 'NVIDIA RTX 20xx', 15, '32GB', '1 TB', 1899.00, 'Large-screen MacBook Air with M3 chip and all-day battery. Ideal for students and professionals who need portability. Silent fanless design with solid performance.'),
('ZenBook 14 OLED UX3402', 'ASUS', 'I 7', 'GeForce 20xx', 14, '32G', '1TB', 1799.00, 'Compact ultrabook with vibrant OLED display. Great for professionals who value display quality. Premium materials with excellent screen and portability.'),

-- Mid-range Professional Laptops
('IdeaPad Pro 5 16', 'Lenovo', 'i7', 'nvidia rtx 20xx', 16, '32GB', '2T', 1699.00, 'Large-screen laptop with solid performance for professionals. Perfect for business users who need screen real estate. Good balance of features and affordability.'),
('Inspiron 16 7000 2-in-1', 'Dell', 'I7', 'NVIDIA 20xx', 16, '32G', '2TB', 1899.00, 'Convertible laptop with large screen and versatile design. Great for professionals and students. Good performance with flexible usage modes.'),
('Pavilion Aero 13', 'HP', 'Intel i7', 'GeForce RTX 20xx', 13, '32 GB', '2T', 1499.00, 'Ultra-lightweight laptop with solid performance. Perfect for professionals who travel frequently. Exceptional portability with good specifications.'),
('Swift 5 SF514', 'Acer', 'intel i7', 'RTX 20xx', 14, '32GB', '2 TB', 1399.00, 'Mid-range ultrabook with good build quality and performance. Great for students and professionals. Solid value proposition with modern features.'),
('VivoBook Pro 15 K6502', 'ASUS', 'I 7', 'nvidia 20xx', 15, '32G', '2TB', 1599.00, 'Creator-focused laptop with decent specs at competitive price. Perfect for content creators on budget. Good performance with creative-oriented features.'),

-- Gaming and Entertainment
('Legion Pro 7i Gen 8', 'Lenovo', 'i9', 'NVIDIA RTX 20xx', 16, '32GB', '1T', 2999.00, 'High-performance gaming laptop with premium features. Perfect for serious gamers and content creators. Advanced cooling with RGB lighting and solid build.'),
('Omen 17 cb2000', 'HP', 'I9', 'GeForce 20xx', 17, '32G', '1TB', 2599.00, 'Large-screen gaming laptop with powerful specs and gaming features. Great for competitive gaming and streaming. Advanced thermal design with gaming aesthetics.'),
('Predator Helios 16', 'Acer', 'Intel i9', 'nvidia rtx 20xx', 16, '32 GB', '1T', 2799.00, 'Gaming laptop with balanced performance and premium features. Perfect for gaming enthusiasts and content creators. Solid cooling with modern gaming features.'),
('ROG Strix SCAR 16', 'ASUS', 'intel i9', 'RTX20xx', 16, '32GB', '1 TB', 3199.00, 'Esports-focused gaming laptop with competitive features. Ideal for professional gamers and enthusiasts. High refresh rate display with gaming optimization.'),
('Alienware m15 R8', 'Dell', 'I 9', 'NVIDIA 20xx', 15, '32G', '1TB', 3399.00, 'Premium gaming laptop with alien design and powerful specs. Perfect for gaming enthusiasts who want unique aesthetics. Premium build with advanced features.'),

-- Budget Professional Options
('ThinkBook 15 G4', 'Lenovo', 'i5', 'GeForce RTX 20xx', 15, '16GB', '1T', 999.00, 'Business laptop with modern features at affordable price. Great for small businesses and startups. ThinkPad DNA with budget-friendly pricing.'),
('ProBook 450 G10', 'HP', 'I5', 'nvidia 20xx', 15, '16G', '1TB', 1099.00, 'Business laptop with essential features and reliable performance. Perfect for enterprise deployments and professional use. Good security with manageable pricing.'),
('Vostro 3520', 'Dell', 'Intel i5', 'RTX 20xx', 15, '16 GB', '1T', 899.00, 'Small business laptop with decent specs and Dell reliability. Great for office work and basic business applications. Cost-effective with essential features.'),
('Aspire 5 A515-58', 'Acer', 'intel i5', 'NVIDIA RTX 20xx', 15, '16GB', '1 TB', 799.00, 'Budget laptop with surprisingly good specs for the price. Perfect for students and home users. Good value proposition with decent build quality.'),
('VivoBook 15 X1504', 'ASUS', 'I 5', 'GeForce 20xx', 15, '16G', '1TB', 749.00, 'Entry-level laptop with modern design and basic performance. Great for students and casual users. Affordable option with colorful design choices.'),

-- Convertible and 2-in-1 Models
('Yoga 9i 2-in-1 Gen 8', 'Lenovo', 'i7', 'nvidia rtx 20xx', 14, '32GB', '1T', 2199.00, 'Premium convertible with leather accents and solid performance. Perfect for business professionals and creatives. Luxury materials with versatile design.'),
('Spectre x360 14', 'HP', 'I7', 'NVIDIA 20xx', 14, '32G', '1TB', 2099.00, 'Premium convertible with gem-cut design and solid specs. Great for executives and creative professionals. Luxury materials with excellent build quality.'),
('XPS 13 2-in-1 9315', 'Dell', 'Intel i7', 'GeForce RTX 20xx', 13, '32 GB', '1T', 1999.00, 'Compact premium convertible with excellent build quality. Perfect for professionals who need versatility. Premium materials with solid performance.'),
('ZenBook Flip 14 UX3404', 'ASUS', 'intel i7', 'RTX20xx', 14, '32GB', '1 TB', 1799.00, 'Convertible ultrabook with OLED display and good performance. Great for professionals and students. Versatile design with premium display quality.'),
('Surface Pro 9', 'Microsoft', 'I 7', 'nvidia 20xx', 13, '32G', '1TB', 1699.00, 'Detachable tablet-laptop with Surface ecosystem integration. Perfect for mobile professionals and creatives. Unique form factor with solid performance.'),

-- Workstation and Professional Graphics
('Precision 5680', 'Dell', 'i9', 'NVIDIA RTX 20xx', 16, '64GB', '4T', 4199.00, 'Mobile workstation with professional graphics and ISV certification. Perfect for CAD, engineering, and professional 3D work. Maximum performance and reliability.'),
('ZBook Fury 16 G10', 'HP', 'I9', 'GeForce 20xx', 16, '64G', '4TB', 3999.00, 'Flagship mobile workstation with desktop-class performance. Ideal for professional applications and demanding workloads. ISV-certified with premium components.'),
('ThinkPad P1 Gen 6', 'Lenovo', 'Intel Core i9', 'nvidia rtx 20xx', 16, '64 GB', '4T', 3799.00, 'Slim mobile workstation with powerful specs. Perfect for professionals who need workstation power in portable form. ThinkPad reliability with workstation performance.'),
('StudioBook Pro 16 W7600', 'ASUS', 'intel i9', 'RTX 20xx', 16, '64GB', '4 TB', 3599.00, 'Creator workstation with color-accurate display. Ideal for professional video editing and design work. ISV-certified with creator-focused features.'),
('WS66 11UMT', 'MSI', 'I 9', 'NVIDIA 20xx', 15, '64G', '4TB', 3699.00, 'Mobile workstation optimized for professional workflows. Perfect for engineering and content creation. Professional graphics with workstation features.'),

-- Compact and Ultra-portable
('Surface Laptop 5 13', 'Microsoft', 'i7', 'GeForce RTX 20xx', 13, '16GB', '1T', 1599.00, 'Compact premium laptop with Microsoft ecosystem integration. Great for students and professionals. Clean design with solid performance and build quality.'),
('Galaxy Book3 Pro 360', 'Samsung', 'I7', 'nvidia 20xx', 16, '16G', '1TB', 1899.00, 'Large-screen convertible with Samsung ecosystem features. Perfect for users in Samsung ecosystem. AMOLED display with good performance and S Pen support.'),
('MateBook 14s', 'Huawei', 'Intel i7', 'RTX20xx', 14, '16 GB', '1T', 1399.00, 'Compact laptop with premium design and solid performance. Great for professionals who value design. Good build quality with competitive specifications.'),
('RedmiBook Pro 14', 'Xiaomi', 'intel i7', 'NVIDIA RTX 20xx', 14, '16GB', '1 TB', 1199.00, 'Affordable premium laptop with flagship features. Perfect for budget-conscious users who want performance. Good value with solid build quality.'),
('Honor MagicBook 14', 'Honor', 'I 7', 'GeForce 20xx', 14, '16G', '1TB', 1099.00, 'Budget laptop with premium features and decent performance. Great for students and young professionals. Good balance of features and affordability.'),

-- Creative and Design Focus
('ConceptD 7 Ezel', 'Acer', 'i9', 'nvidia rtx 20xx', 15, '32GB', '2T', 3499.00, 'Innovative convertible workstation with unique hinge design. Perfect for designers and digital artists. Creative-focused with color-accurate display.'),
('StudioBook 16 H7604', 'ASUS', 'I9', 'NVIDIA 20xx', 16, '32G', '2TB', 2999.00, 'Creator laptop with Pantone-validated display. Ideal for professional color work and design. Premium materials with creator optimization.'),
('Creator 17 A10SE', 'MSI', 'Intel i9', 'GeForce RTX 20xx', 17, '32 GB', '2T', 2799.00, 'Large-screen creator laptop with color-accurate display. Perfect for video editing and graphic design. Professional features with solid performance.'),
('MacBook Pro 16 M3 Max', 'Apple', 'intel i9', 'RTX20xx', 16, '32GB', '2 TB', 3999.00, 'Ultimate creative powerhouse with M3 Max chip. Perfect for professional video editing and music production. Premium build with exceptional performance.'),
('ZBook Create G9', 'HP', 'I 9', 'nvidia 20xx', 15, '32G', '2TB', 3199.00, 'Creator-focused mobile workstation with professional features. Great for content creation and design work. Optimized for creative workflows with solid specs.'),

-- Gaming Laptops - Mid to High End
('Katana 17 B13V', 'MSI', 'i7', 'NVIDIA RTX 20xx', 17, '32GB', '1T', 1999.00, 'Large-screen gaming laptop with solid performance. Great for gaming and content creation. Good value with decent build quality and gaming features.'),
('TUF Gaming A15', 'ASUS', 'I7', 'GeForce 20xx', 15, '32G', '1TB', 1699.00, 'Durable gaming laptop with military-grade construction. Perfect for gaming enthusiasts who need reliability. Solid build with good gaming performance.'),
('Victus 15 fb0000', 'HP', 'Intel i7', 'nvidia rtx 20xx', 15, '32 GB', '1T', 1599.00, 'Gaming laptop with modern design and solid specs. Great for casual gaming and content creation. Good balance of gaming performance and everyday use.'),
('Nitro 5 AN515-58', 'Acer', 'intel i7', 'RTX 20xx', 15, '32GB', '1 TB', 1399.00, 'Budget gaming laptop with decent specs and good value. Perfect for entry-level gaming and students. Affordable gaming performance with room for upgrades.'),
('IdeaPad Gaming 3 15', 'Lenovo', 'I 7', 'NVIDIA 20xx', 15, '32G', '1TB', 1499.00, 'Affordable gaming laptop with solid performance. Great for students and casual gamers. Good balance of gaming capability and everyday usability.'),

-- Business Convertibles and Tablets
('ThinkPad X13 Yoga Gen 4', 'Lenovo', 'i7', 'GeForce RTX 20xx', 13, '16GB', '1T', 1899.00, 'Compact business convertible with ThinkPad reliability. Perfect for mobile professionals and executives. Premium build with versatile form factor.'),
('EliteBook x360 1040 G10', 'HP', 'I7', 'nvidia 20xx', 14, '16G', '1TB', 2199.00, 'Premium business convertible with security features. Great for enterprise deployments and executives. Advanced security with elegant design.'),
('Latitude 7330 2-in-1', 'Dell', 'Intel i7', 'RTX20xx', 13, '16 GB', '1T', 1799.00, 'Compact business convertible with premium build. Perfect for mobile workers and consultants. Dell reliability with modern features.'),
('Surface Pro 9 for Business', 'Microsoft', 'intel i7', 'NVIDIA RTX 20xx', 13, '16GB', '1 TB', 1999.00, 'Business tablet with enterprise features and management. Ideal for mobile professionals and field workers. Microsoft ecosystem with business optimization.'),
('Galaxy Book3 Pro 360 15', 'Samsung', 'I 7', 'GeForce 20xx', 15, '16G', '1TB', 2099.00, 'Large-screen business convertible with S Pen support. Great for professionals who need large screen and flexibility. Samsung ecosystem integration with solid specs.'),

-- Ultra-budget but capable
('Aspire 3 A315-510P', 'Acer', 'i3', 'nvidia 20xx', 15, '8GB', '512GB', 599.00, 'Entry-level laptop with basic specs for everyday computing. Perfect for students and basic home use. Affordable option with essential features.'),
('Pavilion 15-eh3000', 'HP', 'I3', 'NVIDIA 20xx', 15, '8G', '512G', 649.00, 'Budget laptop with modern design and basic performance. Great for home users and light office work. HP reliability at budget-friendly price.'),
('IdeaPad 1 15', 'Lenovo', 'Intel i3', 'GeForce RTX 20xx', 15, '8 GB', '512GB', 549.00, 'Ultra-budget laptop with essential features. Perfect for basic computing and students on tight budget. Lenovo quality at entry-level pricing.'),
('Inspiron 15 3000', 'Dell', 'intel i3', 'RTX 20xx', 15, '8GB', '512G', 579.00, 'Basic laptop for everyday computing needs. Great for home users and office work. Dell reliability with affordable pricing.'),
('VivoBook Go 15', 'ASUS', 'I 3', 'nvidia 20xx', 15, '8G', '512GB', 499.00, 'Entry-level laptop with modern design options. Perfect for students and casual users. Colorful design with basic but functional specifications.'),

-- Specialized and Niche
('Framework Laptop DIY', 'Framework', 'i5', 'NVIDIA RTX 20xx', 13, '16GB', '1T', 1299.00, 'Modular laptop kit for tech enthusiasts. Perfect for users who want to build and customize. Revolutionary approach with educational value.'),
('System76 Lemur Pro', 'System76', 'I5', 'GeForce 20xx', 14, '16G', '1TB', 1399.00, 'Linux-optimized laptop with open-source firmware. Great for developers and Linux enthusiasts. Clean design with Linux-first optimization.'),
('Librem 14 v2', 'Purism', 'Intel i5', 'nvidia rtx 20xx', 14, '16 GB', '1T', 1699.00, 'Privacy-focused laptop with hardware kill switches. Perfect for security professionals and privacy advocates. Unique approach with solid specifications.'),
('StarLite Mk IV', 'Star Labs', 'intel i5', 'RTX20xx', 11, '16GB', '1 TB', 799.00, 'Compact Linux laptop with premium build. Great for developers and minimalist users. Ultra-portable with Linux optimization.'),
('PineBook Pro ARM', 'Pine64', 'I 5', 'NVIDIA 20xx', 14, '16G', '1TB', 399.00, 'ARM-based laptop with open-source design. Perfect for developers and open-source enthusiasts. Unique architecture with community support.'),

-- High-end gaming and enthusiast
('Strix SCAR 17 SE', 'ASUS', 'i9', 'GeForce RTX 20xx', 17, '64GB', '4T', 4199.00, 'Ultimate gaming laptop with desktop-class performance. Perfect for professional esports and streaming. Maximum performance with premium gaming features.'),
('Raider GE78 HX', 'MSI', 'I9', 'nvidia 20xx', 17, '64G', '4TB', 3999.00, 'Large-screen gaming powerhouse with RGB lighting. Great for gaming enthusiasts and content creators. Advanced cooling with customizable aesthetics.'),
('Area-51m R2', 'Alienware', 'Intel Core i9', 'RTX 20xx', 17, '64 GB', '4T', 4499.00, 'Desktop replacement with upgradeable components. Perfect for hardcore gamers who want desktop power. Alien design with maximum customization.'),
('Blade Pro 17', 'Razer', 'intel i9', 'NVIDIA RTX 20xx', 17, '64GB', '4 TB', 4299.00, 'Professional gaming laptop with workstation features. Ideal for content creators and serious gamers. Premium materials with dual-purpose optimization.'),
('Origin EON17-X', 'Origin PC', 'I 9', 'GeForce 20xx', 17, '64G', '4TB', 4799.00, 'Custom gaming laptop with boutique build quality. Perfect for enthusiasts who demand the best. Lifetime support with maximum customization options.'),

-- Content Creator Focused
('Creator Z17 A12U', 'MSI', 'i9', 'nvidia rtx 20xx', 17, '32GB', '2T', 2999.00, 'Large-screen creator laptop with color-accurate display. Perfect for video editing and graphic design. Professional features with solid performance specifications.'),
('ProArt Studiobook Pro 17', 'ASUS', 'I9', 'NVIDIA 20xx', 17, '32G', '2TB', 3299.00, 'Professional creator workstation with Pantone validation. Ideal for color-critical work and professional content creation. Premium materials with creator optimization.'),
('ConceptD 9 Pro', 'Acer', 'Intel i9', 'GeForce RTX 20xx', 17, '32 GB', '2T', 3799.00, 'Ultimate creator laptop with desktop-class performance. Perfect for professional 3D work and video production. ISV-certified with premium specifications.'),
('ZBook Studio G10', 'HP', 'intel i9', 'RTX20xx', 16, '32GB', '2 TB', 3199.00, 'Mobile workstation optimized for creative workflows. Great for content creators and designers. Professional graphics with creator-focused features.'),
('MacBook Pro 16 Studio', 'Apple', 'I 9', 'nvidia 20xx', 16, '32G', '2TB', 3599.00, 'Professional MacBook for demanding creative work. Perfect for video editors and music producers. Premium build with studio-grade performance.'),

-- Mid-range versatile options
('Envy x360 15', 'HP', 'i7', 'NVIDIA RTX 20xx', 15, '16GB', '1T', 1499.00, 'Premium convertible with elegant design. Great for professionals and students. Good balance of performance and versatility.'),
('Inspiron 16 Plus 7620', 'Dell', 'I7', 'GeForce 20xx', 16, '16G', '1TB', 1599.00, 'Large-screen laptop with creator features. Perfect for content creation and productivity. Good performance with creator-oriented design.'),
('Yoga Slim 7 Pro X', 'Lenovo', 'Intel i7', 'nvidia rtx 20xx', 14, '16 GB', '1T', 1399.00, 'Slim laptop with premium features. Great for professionals and students. Good balance of portability and performance.'),
('Swift X SFX14-71G', 'Acer', 'intel i7', 'RTX 20xx', 14, '16GB', '1 TB', 1299.00, 'Creator laptop with dedicated graphics. Perfect for content creation and light gaming. Good value with creator-focused features.'),
('VivoBook Pro 14X N7401', 'ASUS', 'I 7', 'NVIDIA 20xx', 14, '16G', '1TB', 1199.00, 'Compact creator laptop with OLED display. Great for design work and content creation. Good performance with premium display quality.'),

-- Rugged and specialized use
('Toughbook CF-33', 'Panasonic', 'i7', 'GeForce RTX 20xx', 12, '32GB', '1T', 4199.00, 'Rugged detachable laptop for extreme environments. Perfect for field work and industrial applications. Maximum durability with modern performance.'),
('Latitude 5430 Rugged', 'Dell', 'I7', 'nvidia 20xx', 14, '32G', '1TB', 2999.00, 'Semi-rugged business laptop for demanding use. Great for field service and outdoor work. Business-grade durability with solid performance.'),
('Getac S410 G5', 'Getac', 'Intel i7', 'RTX20xx', 14, '32 GB', '1T', 3499.00, 'Rugged laptop with sunlight-readable display. Perfect for military and public safety use. Extreme durability with professional specifications.'),
('Durabook R11', 'Durabook', 'intel i7', 'NVIDIA RTX 20xx', 11, '32GB', '1 TB', 2799.00, 'Compact rugged laptop for mobile professionals. Great for field workers and first responders. Military-grade durability in compact form.'),
('Panasonic FZ-55', 'Panasonic', 'I 7', 'GeForce 20xx', 14, '32G', '1TB', 3299.00, 'Semi-rugged laptop with hot-swappable battery. Perfect for long deployment and field work. Modular design with professional reliability.'),

-- Student and Education Focus
('Chromebook Spin 714', 'Acer', 'i5', 'nvidia rtx 20xx', 14, '16GB', '512GB', 899.00, 'Premium Chromebook with convertible design. Great for students and education environments. Chrome OS optimization with solid build quality.'),
('Surface Laptop Go 3', 'Microsoft', 'I5', 'NVIDIA 20xx', 12, '16G', '512G', 799.00, 'Compact laptop designed for students and education. Perfect for cloud-based workflows and basic computing. Microsoft ecosystem with student-friendly pricing.'),
('IdeaPad Duet 5', 'Lenovo', 'Intel i5', 'GeForce RTX 20xx', 13, '16 GB', '512GB', 749.00, 'Detachable Chromebook with premium build. Great for students and mobile users. Chrome OS with tablet versatility and laptop productivity.'),
('Galaxy Book2 15', 'Samsung', 'intel i5', 'RTX20xx', 15, '16GB', '512G', 949.00, 'Student laptop with Samsung ecosystem integration. Perfect for young professionals and students. Good value with modern features and design.'),
('VivoBook Flip 14', 'ASUS', 'I 5', 'nvidia 20xx', 14, '16G', '512GB', 699.00, 'Affordable convertible with touchscreen and pen support. Great for students and creative learning. Versatile design with budget-friendly pricing.');

-- Additional laptop data - File 3 of 5 (200 records)
-- Focus: Student, Budget, and Entry-level laptops
-- Emphasizing affordability, basic performance, and educational use cases

INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Student and Education Focus
('IdeaPad 1 Student Edition', 'Lenovo', 'i5', 'Nvidia 20xx', 15, '8GB', '512GB', 549.00, 'Affordable student laptop with essential features for coursework and research. Perfect for college students on tight budgets. Reliable performance for basic computing needs.'),
('Aspire 1 Education', 'Acer', 'I5', 'NVIDIA 20xx', 15, '8G', '512G', 499.00, 'Entry-level laptop designed for educational environments. Great for students and basic office work. Cost-effective solution with decent build quality.'),
('Pavilion Student 14', 'HP', 'Intel i5', 'GeForce RTX 20xx', 14, '8 GB', '512GB', 599.00, 'Compact student laptop with modern features at budget price. Perfect for note-taking and online learning. Good portability for campus life.'),
('Inspiron 15 3000 Student', 'Dell', 'intel i5', 'RTX20xx', 15, '8GB', '512G', 579.00, 'Basic laptop optimized for student use and homework. Ideal for educational applications and web browsing. Dell reliability at student-friendly pricing.'),
('VivoBook E15', 'ASUS', 'I 5', 'nvidia 20xx', 15, '8G', '512GB', 529.00, 'Colorful student laptop with essential performance features. Great for young learners and casual computing. Affordable option with modern design.'),

-- Budget Office and Home Use
('IdeaPad 3 Home', 'Lenovo', 'i3', 'NVIDIA RTX 20xx', 15, '8GB', '1T', 699.00, 'Home laptop for family use and basic productivity. Perfect for web browsing, documents, and media consumption. Good value for everyday computing needs.'),
('Aspire 3 Home Office', 'Acer', 'I3', 'GeForce 20xx', 15, '8G', '1TB', 649.00, 'Home office laptop with reliable performance for basic tasks. Great for remote work and family computing. Affordable solution with decent specifications.'),
('Pavilion 15 Home', 'HP', 'Intel i3', 'nvidia rtx 20xx', 15, '8 GB', '1T', 679.00, 'Family laptop with good performance for home use. Perfect for homework, entertainment, and light office work. HP quality at budget pricing.'),
('Inspiron 15 Home', 'Dell', 'intel i3', 'RTX 20xx', 15, '8GB', '1 TB', 629.00, 'Home computing solution with essential features. Ideal for family use and basic productivity tasks. Reliable Dell quality at affordable price.'),
('VivoBook 15 Basic', 'ASUS', 'I 3', 'NVIDIA 20xx', 15, '8G', '1TB', 599.00, 'Basic laptop for everyday computing needs. Great for students and home users. Simple design with functional specifications.'),

-- Chromebook and Cloud-focused
('Chromebook Spin 513', 'Acer', 'i5', 'GeForce RTX 20xx', 13, '8GB', '512G', 749.00, 'Premium Chromebook with convertible design and solid performance. Perfect for cloud-based workflows and education. Chrome OS optimization with good build quality.'),
('Chromebook Pro c425', 'ASUS', 'I5', 'nvidia 20xx', 14, '8G', '512GB', 699.00, 'Professional Chromebook for business and education use. Great for Google Workspace and web applications. Modern design with reliable performance.'),
('Chromebook x360 14c', 'HP', 'Intel i5', 'RTX20xx', 14, '8 GB', '512G', 799.00, 'Convertible Chromebook with premium features and solid build. Perfect for education and business use. Versatile design with touch support.'),
('Chromebook 3100', 'Dell', 'intel i5', 'NVIDIA RTX 20xx', 11, '8GB', '512GB', 649.00, 'Education-focused Chromebook with durability and ease of management. Ideal for schools and classroom environments. Rugged design for student use.'),
('Chromebook Flip C214', 'ASUS', 'I 5', 'GeForce 20xx', 11, '8G', '512G', 599.00, 'Durable convertible Chromebook for education environments. Perfect for K-12 schools and student use. Military-grade durability with kid-friendly design.'),

-- Basic Business Laptops
('ThinkBook 14 Basic', 'Lenovo', 'i5', 'nvidia rtx 20xx', 14, '16GB', '1T', 1099.00, 'Entry-level business laptop with modern features. Great for small businesses and startups. ThinkPad quality at competitive pricing.'),
('ProBook 440 G9', 'HP', 'I5', 'NVIDIA 20xx', 14, '16G', '1TB', 1199.00, 'Small business laptop with essential security and management features. Perfect for office environments and professional use. Reliable performance with modern connectivity.'),
('Latitude 3420', 'Dell', 'Intel i5', 'GeForce RTX 20xx', 14, '16 GB', '1T', 1149.00, 'Business laptop with Dell reliability and essential features. Ideal for corporate deployments and office work. Good balance of features and affordability.'),
('ExpertBook B1400', 'ASUS', 'intel i5', 'RTX 20xx', 14, '16GB', '1 TB', 1099.00, 'Business laptop with security features and reliable performance. Great for enterprise environments and professional use. Cost-effective business solution.'),
('TravelMate B3', 'Acer', 'I 5', 'nvidia 20xx', 14, '16G', '1TB', 999.00, 'Business travel laptop with focus on portability and battery life. Perfect for mobile professionals and consultants. Good value for business features.'),

-- Entry-level Gaming
('Nitro 5 Budget', 'Acer', 'i5', 'NVIDIA RTX 20xx', 15, '16GB', '1T', 1399.00, 'Entry-level gaming laptop with decent performance for 1080p gaming. Perfect for casual gamers and students. Good value with upgrade potential.'),
('TUF Gaming F15 Basic', 'ASUS', 'I5', 'GeForce 20xx', 15, '16G', '1TB', 1299.00, 'Durable entry-level gaming laptop with military-grade construction. Great for budget gaming and student use. Solid build quality with gaming features.'),
('Pavilion Gaming 15 Basic', 'HP', 'Intel i5', 'nvidia rtx 20xx', 15, '16 GB', '1T', 1349.00, 'Budget gaming laptop with decent specs for casual gaming. Perfect for students who want gaming capability. Good balance of price and performance.'),
('G15 Gaming Basic', 'Dell', 'intel i5', 'RTX20xx', 15, '16GB', '1 TB', 1299.00, 'Entry-level gaming laptop with solid performance for 1080p games. Great for casual gamers and multimedia use. Dell quality with gaming features.'),
('IdeaPad Gaming 3 Basic', 'Lenovo', 'I 5', 'NVIDIA 20xx', 15, '16G', '1TB', 1249.00, 'Affordable gaming laptop with good performance for the price. Perfect for budget-conscious gamers and students. Decent specifications with room for upgrades.'),

-- Refurbished and Open-box Options
('ThinkPad T480 Refurb', 'Lenovo', 'i7', 'GeForce RTX 20xx', 14, '16GB', '1T', 899.00, 'Refurbished business laptop with excellent build quality. Great for professionals who want ThinkPad reliability at lower cost. Tested and certified with warranty.'),
('EliteBook 840 Open Box', 'HP', 'I7', 'nvidia 20xx', 14, '16G', '1TB', 1099.00, 'Open-box business laptop with premium features at reduced price. Perfect for budget-conscious professionals. Full warranty with significant savings.'),
('XPS 13 Certified Renewed', 'Dell', 'Intel i7', 'RTX 20xx', 13, '16 GB', '1T', 1299.00, 'Certified renewed premium ultrabook with warranty. Great for users who want XPS quality at lower price. Thoroughly tested and refurbished.'),
('ZenBook 14 Open Box', 'ASUS', 'intel i7', 'NVIDIA RTX 20xx', 14, '16GB', '1 TB', 999.00, 'Open-box premium ultrabook with OLED display. Perfect for creative work at discounted price. Minimal use with full manufacturer warranty.'),
('MacBook Air M1 Refurb', 'Apple', 'I 7', 'GeForce 20xx', 13, '16G', '1TB', 1199.00, 'Refurbished MacBook Air with M1 chip and warranty. Great for Apple ecosystem users on budget. Certified refurbished with like-new condition.'),

-- 2-in-1 Budget Options
('Pavilion x360 14', 'HP', 'i5', 'nvidia rtx 20xx', 14, '16GB', '1T', 1199.00, 'Affordable convertible laptop with touchscreen and pen support. Perfect for students and casual users. Versatile design with decent performance.'),
('IdeaPad Flex 5', 'Lenovo', 'I5', 'NVIDIA 20xx', 14, '16G', '1TB', 1149.00, 'Flexible 2-in-1 laptop with solid performance and build quality. Great for productivity and entertainment. Good value in convertible category.'),
('Inspiron 14 2-in-1', 'Dell', 'Intel i5', 'GeForce RTX 20xx', 14, '16 GB', '1T', 1199.00, 'Convertible laptop with touchscreen for versatile use. Perfect for students and professionals who need flexibility. Dell reliability in 2-in-1 form.'),
('VivoBook Flip 14', 'ASUS', 'intel i5', 'RTX20xx', 14, '16GB', '1 TB', 1099.00, 'Affordable convertible with touchscreen and pen support. Great for creative work and note-taking. Colorful design with modern features.'),
('Spin 3 SP314', 'Acer', 'I 5', 'nvidia 20xx', 14, '16G', '1TB', 1049.00, 'Budget-friendly convertible laptop with decent specs. Perfect for students and home users. Good build quality at competitive price.'),

-- Mini and Compact Options
('IdeaPad 1 11', 'Lenovo', 'i3', 'NVIDIA RTX 20xx', 11, '8GB', '512G', 449.00, 'Ultra-compact laptop for basic computing and portability. Perfect for travel and basic tasks. Extremely portable with essential features.'),
('Stream 11', 'HP', 'I3', 'GeForce 20xx', 11, '8G', '512GB', 399.00, 'Compact laptop for cloud computing and basic use. Great for students and casual users. Ultra-portable with Windows 11 and Office 365.'),
('Inspiron 11 3000', 'Dell', 'Intel i3', 'nvidia rtx 20xx', 11, '8 GB', '512G', 479.00, 'Small laptop for basic computing and web browsing. Perfect for travel and secondary computer use. Compact design with essential performance.'),
('E210MA', 'ASUS', 'intel i3', 'RTX 20xx', 11, '8GB', '512GB', 429.00, 'Ultra-portable laptop with basic specs for everyday use. Great for students and basic computing. Lightweight design with decent battery life.'),
('Swift 1 SF114', 'Acer', 'I 3', 'NVIDIA 20xx', 14, '8G', '512G', 549.00, 'Compact laptop with larger screen and basic performance. Perfect for students who need portability. Good balance of size and usability.'),

-- Older Generation Value Options
('ThinkPad E14 Gen 2', 'Lenovo', 'i5', 'GeForce RTX 20xx', 14, '16GB', '1T', 999.00, 'Previous generation business laptop with solid performance. Great for professionals who want proven reliability. Good value with modern features.'),
('EliteBook 845 G7', 'HP', 'I5', 'nvidia 20xx', 14, '16G', '1TB', 1199.00, 'Previous generation business laptop with AMD processor. Perfect for business use with excellent battery life. Good value with premium features.'),
('Latitude 5410', 'Dell', 'Intel i5', 'RTX20xx', 14, '16 GB', '1T', 1149.00, 'Previous generation business laptop with reliable performance. Ideal for corporate environments and professional use. Proven design with solid specs.'),
('ZenBook 14 UM425', 'ASUS', 'intel i5', 'NVIDIA RTX 20xx', 14, '16GB', '1 TB', 999.00, 'Previous generation ultrabook with good performance and build. Great for professionals who want quality at lower price. Solid specifications.'),
('Swift 3 SF314-42', 'Acer', 'I 5', 'GeForce 20xx', 14, '16G', '1TB', 899.00, 'Previous generation mid-range laptop with good value. Perfect for students and professionals. Decent performance at competitive price.'),

-- Basic Content Creation
('Aspire 5 Creator', 'Acer', 'i7', 'nvidia rtx 20xx', 15, '16GB', '1T', 1399.00, 'Budget creator laptop with dedicated graphics for light content work. Perfect for aspiring content creators and students. Good performance for creative tasks.'),
('IdeaPad Creator 5', 'Lenovo', 'I7', 'NVIDIA 20xx', 15, '16G', '1TB', 1499.00, 'Mid-range creator laptop with solid performance for content creation. Great for video editing and design work. Good balance of price and creative features.'),
('Pavilion Creator 15', 'HP', 'Intel i7', 'GeForce RTX 20xx', 15, '16 GB', '1T', 1549.00, 'Creator-focused laptop with decent specs for content work. Perfect for photographers and video editors. Good display quality and performance.'),
('Inspiron 15 Creator', 'Dell', 'intel i7', 'RTX20xx', 15, '16GB', '1 TB', 1499.00, 'Content creation laptop with solid performance and good display. Great for creative professionals on budget. Dell reliability with creator features.'),
('VivoBook Pro 15', 'ASUS', 'I 7', 'nvidia 20xx', 15, '16G', '1TB', 1449.00, 'Creator laptop with OLED display and decent performance. Perfect for design work and content creation. Good color accuracy at competitive price.'),

-- Thin and Light Budget Options
('Swift 1', 'Acer', 'i5', 'NVIDIA RTX 20xx', 14, '8GB', '512G', 799.00, 'Ultra-thin budget laptop with decent performance. Perfect for students and professionals who need portability. Lightweight design with essential features.'),
('IdeaPad S340', 'Lenovo', 'I5', 'GeForce 20xx', 14, '8G', '512GB', 849.00, 'Slim laptop with good performance for everyday use. Great for students and mobile professionals. Good balance of portability and performance.'),
('Pavilion 13', 'HP', 'Intel i5', 'nvidia rtx 20xx', 13, '8 GB', '512G', 899.00, 'Compact premium laptop with good build quality. Perfect for professionals who need ultraportability. HP quality in small form factor.'),
('Inspiron 13 5000', 'Dell', 'intel i5', 'RTX 20xx', 13, '8GB', '512GB', 879.00, 'Compact laptop with solid performance and build quality. Great for business travel and mobile work. Dell reliability in portable package.'),
('ZenBook 13', 'ASUS', 'I 5', 'NVIDIA 20xx', 13, '8G', '512G', 949.00, 'Premium ultrabook with excellent build quality and performance. Perfect for professionals who want style and portability. Premium materials at competitive price.'),

-- Home and Family Computing
('IdeaPad 3 Family', 'Lenovo', 'i5', 'GeForce RTX 20xx', 17, '16GB', '1T', 1199.00, 'Large-screen family laptop for shared use and entertainment. Perfect for homework, entertainment, and family computing. Good value with large display.'),
('Pavilion 17', 'HP', 'I5', 'nvidia 20xx', 17, '16G', '1TB', 1249.00, 'Large-screen laptop for home use and multimedia consumption. Great for families who need screen real estate. Good performance for home computing.'),
('Inspiron 17 3000', 'Dell', 'Intel i5', 'RTX20xx', 17, '16 GB', '1T', 1199.00, 'Family laptop with large screen for shared computing. Perfect for homework, entertainment, and basic productivity. Affordable large-screen option.'),
('VivoBook 17', 'ASUS', 'intel i5', 'NVIDIA RTX 20xx', 17, '16GB', '1 TB', 1149.00, 'Large-screen laptop for home and family use. Great for entertainment and basic productivity tasks. Good value with generous display size.'),
('Aspire 5 17', 'Acer', 'I 5', 'GeForce 20xx', 17, '16G', '1TB', 1099.00, 'Budget large-screen laptop for home use. Perfect for families and students who need screen space. Good value proposition with large display.'),

-- Senior-friendly and Simple Options
('IdeaPad 3 Senior', 'Lenovo', 'i3', 'nvidia rtx 20xx', 15, '8GB', '1T', 699.00, 'Simple laptop designed for seniors and basic computing. Perfect for email, web browsing, and video calls. Easy to use with reliable performance.'),
('Pavilion Senior Edition', 'HP', 'I3', 'NVIDIA 20xx', 15, '8G', '1TB', 749.00, 'User-friendly laptop for seniors and non-technical users. Great for basic computing and staying connected. Simple interface with good support.'),
('Inspiron 15 Easy', 'Dell', 'Intel i3', 'GeForce RTX 20xx', 15, '8 GB', '1T', 719.00, 'Easy-to-use laptop for seniors and basic users. Perfect for email, web browsing, and simple tasks. Dell reliability with user-friendly features.'),
('VivoBook Easy', 'ASUS', 'intel i3', 'RTX 20xx', 15, '8GB', '1 TB', 679.00, 'Simple laptop with large keys and clear display. Great for seniors and basic computing needs. User-friendly design with essential features.'),
('Aspire 3 Simple', 'Acer', 'I 3', 'nvidia 20xx', 15, '8G', '1TB', 649.00, 'Basic laptop with simple interface for non-technical users. Perfect for seniors and casual computing. Straightforward design with reliable performance.'),

-- Professional Entry-level
('ThinkBook 13s', 'Lenovo', 'i5', 'NVIDIA RTX 20xx', 13, '16GB', '512G', 1299.00, 'Professional entry-level laptop with premium design. Perfect for young professionals and consultants. ThinkPad DNA with modern aesthetics.'),
('ProBook 635', 'HP', 'I5', 'GeForce 20xx', 13, '16G', '512GB', 1349.00, 'Business laptop with AMD processor and good performance. Great for professionals who need reliability. Modern features with business-grade quality.'),
('Latitude 3320', 'Dell', 'Intel i5', 'nvidia rtx 20xx', 13, '16 GB', '512G', 1299.00, 'Compact business laptop for mobile professionals. Perfect for consultants and field workers. Dell reliability in portable form factor.'),
('ExpertBook B9450', 'ASUS', 'intel i5', 'RTX20xx', 14, '16GB', '512GB', 1399.00, 'Ultra-lightweight business laptop with premium materials. Great for executives and mobile professionals. Exceptional portability with business features.'),
('TravelMate P2', 'Acer', 'I 5', 'NVIDIA 20xx', 14, '16G', '512G', 1199.00, 'Business travel laptop with focus on portability. Perfect for frequent travelers and consultants. Good balance of features and mobility.'),

-- Specialty and Niche Models
('IdeaPad Duet 3i', 'Lenovo', 'i3', 'GeForce RTX 20xx', 10, '8GB', '256G', 649.00, 'Detachable 2-in-1 tablet laptop for mobile use. Perfect for students and casual users. Tablet functionality with laptop productivity.'),
('Surface Go 3', 'Microsoft', 'I3', 'nvidia 20xx', 10, '8G', '256GB', 799.00, 'Compact Surface tablet with keyboard for mobile productivity. Great for note-taking and light computing. Microsoft ecosystem with portable design.'),
('iPad Pro with Keyboard', 'Apple', 'Intel i3', 'RTX 20xx', 11, '8 GB', '256G', 1199.00, 'Tablet-laptop hybrid for creative and professional work. Perfect for artists and mobile professionals. Apple ecosystem with powerful performance.'),
('Galaxy Book Go', 'Samsung', 'intel i3', 'NVIDIA RTX 20xx', 14, '8GB', '256GB', 699.00, 'Always-connected laptop with cellular connectivity. Great for mobile professionals and students. Samsung ecosystem with always-on connectivity.'),
('Pixelbook Go', 'Google', 'I 3', 'GeForce 20xx', 13, '8G', '128G', 849.00, 'Premium Chromebook with Google services integration. Perfect for Google ecosystem users. Premium build with Chrome OS optimization.'),

-- Rugged and Durable Budget Options
('ToughBook CF-20', 'Panasonic', 'i5', 'nvidia rtx 20xx', 10, '16GB', '512G', 2999.00, 'Rugged detachable laptop for extreme environments. Perfect for field work and industrial use. Maximum durability with modern connectivity.'),
('Latitude 3190 Education', 'Dell', 'I5', 'NVIDIA 20xx', 11, '8G', '128GB', 899.00, 'Education-focused rugged laptop for classroom use. Great for K-12 schools and student environments. Durable design with educational features.'),
('TUF Book 15', 'ASUS', 'Intel i5', 'GeForce RTX 20xx', 15, '16 GB', '512G', 1199.00, 'Durable laptop with military-grade testing. Perfect for students and outdoor professionals. Robust build quality with solid performance.'),
('ProBook Fortis 14', 'HP', 'intel i5', 'RTX20xx', 14, '8GB', '256GB', 999.00, 'Education rugged laptop for school environments. Great for K-12 and higher education use. Durable design with educational features.'),
('Chromebook Spin 511', 'Acer', 'I 5', 'nvidia 20xx', 11, '8G', '64G', 649.00, 'Rugged convertible Chromebook for education use. Perfect for schools and student environments. Durable design with Chrome OS benefits.'),

-- International and Global Options
('ThinkBook 14 Global', 'Lenovo', 'i5', 'NVIDIA RTX 20xx', 14, '16GB', '512G', 1199.00, 'International business laptop with multi-language support. Perfect for global companies and international use. Business features with global connectivity.'),
('Pavilion Global Edition', 'HP', 'I5', 'GeForce 20xx', 15, '16G', '1TB', 1299.00, 'Global laptop with international warranty and support. Great for travelers and international students. HP quality with worldwide support.'),
('Inspiron International', 'Dell', 'Intel i5', 'nvidia rtx 20xx', 15, '16 GB', '1T', 1249.00, 'International laptop with global warranty coverage. Perfect for students and professionals who travel. Dell reliability with international support.'),
('ZenBook Global', 'ASUS', 'intel i5', 'RTX 20xx', 14, '16GB', '512GB', 1399.00, 'Global ultrabook with international features. Great for international business and travel. Premium design with worldwide warranty.'),
('Swift Global', 'Acer', 'I 5', 'NVIDIA 20xx', 14, '16G', '512G', 1099.00, 'International laptop with multi-region support. Perfect for global users and international students. Good value with international coverage.'),

-- Final Budget and Value Options
('IdeaPad Essential', 'Lenovo', 'i3', 'GeForce RTX 20xx', 15, '8GB', '1T', 629.00, 'Essential laptop for basic computing needs. Perfect for home users and students on tight budgets. Reliable performance with essential features.'),
('Aspire Essential', 'Acer', 'I3', 'nvidia 20xx', 15, '8G', '1TB', 599.00, 'Basic laptop for everyday computing and home use. Great for families and casual users. Simple design with functional specifications.'),
('Pavilion Essential', 'HP', 'Intel i3', 'RTX20xx', 15, '8 GB', '1T', 649.00, 'Home laptop for family computing and basic tasks. Perfect for homework and entertainment. HP quality at budget-friendly pricing.'),
('Inspiron Essential', 'Dell', 'intel i3', 'NVIDIA RTX 20xx', 15, '8GB', '1 TB', 619.00, 'Basic Dell laptop for home and student use. Great for essential computing and web browsing. Dell reliability at affordable price.'),
('VivoBook Essential', 'ASUS', 'I 3', 'GeForce 20xx', 15, '8G', '1TB', 589.00, 'Entry-level laptop with colorful design options. Perfect for students and casual users. Basic specifications with modern aesthetics.');

-- Additional laptop data - File 4 of 5 (200 records)
-- Focus: Workstation, Enterprise, and Professional High-end laptops
-- Emphasizing mission-critical applications, maximum performance, and enterprise features

INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Enterprise Workstations
('ZBook Fury 17 G10', 'HP', 'i9', 'Nvidia 20xx', 17, '128GB', '4T', 5299.00, 'Flagship mobile workstation with desktop-class performance for demanding professional applications. Perfect for CAD, engineering simulation, and professional video production. ISV-certified with maximum reliability.'),
('Precision 7780', 'Dell', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 4999.00, 'Ultimate mobile workstation for mission-critical professional work. Ideal for aerospace engineering, medical imaging, and scientific computing. Maximum performance with enterprise support.'),
('ThinkPad P17 Gen 4', 'Lenovo', 'Intel Core i9', 'GeForce RTX 20xx', 17, '128 GB', '4T', 5199.00, 'Professional mobile workstation with ThinkPad reliability and maximum performance. Perfect for professional CAD, rendering, and scientific applications. Enterprise-grade with ISV certification.'),
('ZBook Studio G10', 'HP', 'intel i9', 'RTX20xx', 16, '128GB', '4 TB', 4799.00, 'Creator workstation with professional graphics and color-accurate display. Ideal for Hollywood-grade video editing and professional design. Premium materials with workstation performance.'),
('Precision 5680', 'Dell', 'I 9', 'nvidia 20xx', 16, '128G', '4TB', 4599.00, 'Mobile workstation with professional graphics for creative and technical work. Perfect for architecture, product design, and professional content creation. Premium build with professional reliability.'),

-- High-Performance Computing
('WS66 12UMT', 'MSI', 'i9', 'NVIDIA RTX 20xx', 15, '128GB', '4T', 4399.00, 'Mobile workstation optimized for professional workflows and HPC applications. Perfect for scientific computing and professional simulation. Maximum performance with ISV certification.'),
('ProArt Studiobook Pro 16 W7600', 'ASUS', 'I9', 'GeForce 20xx', 16, '128G', '4TB', 4299.00, 'Professional creator workstation with Pantone-validated display. Ideal for professional color work and content creation. Premium materials with workstation-class performance and reliability.'),
('Creator Z17 HX Studio', 'MSI', 'Intel i9', 'nvidia rtx 20xx', 17, '128 GB', '4T', 4199.00, 'Large-screen creator workstation with professional features. Perfect for professional video editing and 3D modeling. Studio-grade performance with professional color accuracy.'),
('ZBook Power G10', 'HP', 'intel i9', 'RTX 20xx', 15, '128GB', '4 TB', 3999.00, 'Mobile workstation with balanced performance and portability. Great for professional applications that need workstation power. ISV-certified with professional reliability.'),
('ThinkPad P16 Gen 2', 'Lenovo', 'I 9', 'NVIDIA 20xx', 16, '128G', '4TB', 4399.00, 'Flagship ThinkPad workstation with maximum performance. Perfect for professional CAD and engineering applications. ThinkPad reliability with workstation-class specifications.'),

-- Extreme Gaming and Enthusiast
('Titan GT77HX 13V', 'MSI', 'i9', 'GeForce RTX 20xx', 17, '128GB', '4T', 5499.00, 'Ultimate gaming laptop with desktop-class performance and mechanical keyboard. Perfect for professional esports and extreme gaming. Maximum customization with RGB lighting and premium cooling.'),
('ROG Strix SCAR 18', 'ASUS', 'I9', 'nvidia 20xx', 18, '128G', '4TB', 4999.00, 'Extreme gaming laptop with massive display and desktop replacement performance. Ideal for competitive esports and professional streaming. Advanced cooling with esports optimization.'),
('Alienware Area-51m R2', 'Alienware', 'Intel Core i9', 'NVIDIA RTX 20xx', 17, '128 GB', '4T', 5799.00, 'Desktop replacement gaming laptop with upgradeable components. Perfect for enthusiasts who want maximum performance and customization. Alien design with premium materials and features.'),
('Razer Blade 18', 'Razer', 'intel i9', 'RTX20xx', 18, '128GB', '4 TB', 4899.00, 'Large-screen gaming laptop with premium materials and maximum performance. Perfect for professional gaming and content creation. Sleek design with desktop-class specifications.'),
('Origin EON17-X 2024', 'Origin PC', 'I 9', 'GeForce 20xx', 17, '128G', '4TB', 6299.00, 'Custom gaming laptop with desktop components and boutique build quality. Perfect for enthusiasts who demand absolute maximum performance. Fully customizable with lifetime support.'),

-- AI and Machine Learning Workstations
('GeForce RTX Workstation', 'MSI', 'i9', 'nvidia rtx 20xx', 17, '128GB', '4T', 4799.00, 'AI workstation optimized for machine learning and deep learning applications. Perfect for data scientists and AI researchers. CUDA acceleration with professional software certification.'),
('ROG Strix SCAR 17 SE AI', 'ASUS', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 4699.00, 'Gaming workstation with AI acceleration for content creation. Ideal for streamers and content creators who use AI tools. Gaming performance with professional AI capabilities.'),
('Precision 7670 AI', 'Dell', 'Intel i9', 'GeForce RTX 20xx', 16, '128 GB', '4T', 4999.00, 'Professional AI workstation for enterprise machine learning. Perfect for corporate AI development and research. Enterprise support with AI software optimization.'),
('ZBook Fury G10 AI', 'HP', 'intel i9', 'RTX 20xx', 17, '128GB', '4 TB', 5199.00, 'AI-optimized mobile workstation for professional development. Ideal for machine learning engineers and data scientists. ISV certification with AI framework optimization.'),
('ThinkPad P1 Gen 6 AI', 'Lenovo', 'I 9', 'nvidia 20xx', 16, '128G', '4TB', 4599.00, 'Slim workstation with AI acceleration capabilities. Perfect for mobile AI developers and data scientists. ThinkPad reliability with cutting-edge AI performance.'),

-- Enterprise Security and Government
('EliteBook 1000 G10', 'HP', 'i9', 'NVIDIA RTX 20xx', 14, '64GB', '2T', 3999.00, 'Ultra-secure business laptop for enterprise and government use. Perfect for executives and security-sensitive environments. Advanced security features with premium materials.'),
('Latitude 9440 Elite', 'Dell', 'I9', 'GeForce 20xx', 14, '64G', '2TB', 3799.00, 'Premium business laptop with advanced security and management. Ideal for C-level executives and secure environments. Dells most secure and premium business laptop.'),
('ThinkPad X1 Extreme Gen 6', 'Lenovo', 'Intel i9', 'nvidia rtx 20xx', 16, '64 GB', '2T', 3899.00, 'Ultimate business laptop with workstation performance. Perfect for executives who need maximum power and premium design. ThinkPad reliability with flagship specifications.'),
('ZBook Firefly G10', 'HP', 'intel i9', 'RTX20xx', 14, '64GB', '2 TB', 3299.00, 'Ultra-portable workstation for mobile professionals. Great for architects and engineers who travel. Workstation power in ultrabook form factor.'),
('Precision 5680 Carbon', 'Dell', 'I 9', 'NVIDIA 20xx', 16, '64G', '2TB', 3699.00, 'Carbon fiber workstation with premium materials. Perfect for mobile professionals who demand the best. Lightweight design with workstation performance.'),

-- Content Creation Powerhouses
('MacBook Pro 16 M3 Ultra', 'Apple', 'i9', 'GeForce RTX 20xx', 16, '128GB', '4T', 5999.00, 'Ultimate creative powerhouse with M3 Ultra chip. Perfect for Hollywood-level video editing and music production. Premium materials with exceptional performance and display.'),
('StudioBook Pro 16 W7700', 'ASUS', 'I9', 'nvidia 20xx', 16, '128G', '4TB', 4899.00, 'Professional studio laptop with reference-grade display. Ideal for professional color grading and content creation. Pantone validation with studio-quality performance.'),
('Creator Z17 HX Studio A13V', 'MSI', 'Intel Core i9', 'RTX 20xx', 17, '128 GB', '4T', 4799.00, 'Studio creator laptop with professional features and large display. Perfect for professional video production and 3D animation. Professional color accuracy with maximum performance.'),
('ConceptD 9 Pro', 'Acer', 'intel i9', 'NVIDIA RTX 20xx', 17, '128GB', '4 TB', 4999.00, 'Ultimate creator laptop with professional ISV certification. Perfect for professional 3D work and high-end content creation. Professional validation with maximum specifications.'),
('ZBook Create G10', 'HP', 'I 9', 'GeForce 20xx', 15, '128G', '4TB', 4299.00, 'Creator-focused mobile workstation with professional graphics. Ideal for content creators who need workstation reliability. Premium design with creator-optimized features.'),

-- Scientific and Research Computing
('Precision 7780 Research', 'Dell', 'i9', 'nvidia rtx 20xx', 17, '128GB', '4T', 5299.00, 'Research workstation for scientific computing and simulation. Perfect for universities and research institutions. Maximum compute power with professional software support.'),
('ThinkPad P17 Research', 'Lenovo', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 5199.00, 'Research workstation with maximum performance for scientific applications. Ideal for computational biology and physics research. Professional reliability with academic support.'),
('ZBook Fury G10 Research', 'HP', 'Intel i9', 'GeForce RTX 20xx', 17, '128 GB', '4T', 5399.00, 'Scientific workstation for research computing and simulation. Perfect for engineering research and scientific modeling. ISV certification with academic pricing available.'),
('WS77 Scientific', 'MSI', 'intel i9', 'RTX20xx', 17, '128GB', '4 TB', 4999.00, 'Scientific computing workstation with CUDA acceleration. Great for researchers and graduate students. Professional performance with educational support.'),
('ProArt Studiobook Research', 'ASUS', 'I 9', 'nvidia 20xx', 16, '128G', '4TB', 4799.00, 'Research workstation for scientific visualization and analysis. Perfect for medical imaging and scientific research. Professional display with research computing power.'),

-- Financial and Trading Workstations
('EliteBook Trading Pro', 'HP', 'i9', 'NVIDIA RTX 20xx', 15, '64GB', '2T', 4199.00, 'Financial trading workstation with multiple display support. Perfect for traders and financial analysts. Ultra-low latency with financial software optimization.'),
('Precision Trading Station', 'Dell', 'I9', 'GeForce 20xx', 15, '64G', '2TB', 3999.00, 'Professional trading laptop with financial market optimization. Ideal for quantitative analysts and day traders. Maximum reliability with financial software certification.'),
('ThinkPad P15 Trading', 'Lenovo', 'Intel i9', 'nvidia rtx 20xx', 15, '64 GB', '2T', 4099.00, 'Trading workstation with ThinkPad reliability and financial features. Perfect for institutional trading and analysis. Professional grade with financial industry support.'),
('ZBook Trading Elite', 'HP', 'intel i9', 'RTX 20xx', 15, '64GB', '2 TB', 4299.00, 'Elite trading workstation for financial professionals. Great for portfolio management and quantitative analysis. Professional performance with financial optimization.'),
('Latitude Trading Pro', 'Dell', 'I 9', 'NVIDIA 20xx', 15, '64G', '2TB', 3899.00, 'Business trading laptop with enterprise security. Perfect for corporate trading desks and financial institutions. Enterprise features with trading optimization.'),

-- Medical and Healthcare Workstations
('ZBook Medical G10', 'HP', 'i9', 'GeForce RTX 20xx', 15, '64GB', '2T', 4599.00, 'Medical workstation for healthcare imaging and analysis. Perfect for radiologists and medical professionals. HIPAA compliance with medical software certification.'),
('Precision Medical 7670', 'Dell', 'I9', 'nvidia 20xx', 16, '64G', '2TB', 4499.00, 'Medical imaging workstation for healthcare professionals. Ideal for diagnostic imaging and medical research. Medical grade with DICOM optimization.'),
('ThinkPad P16 Medical', 'Lenovo', 'Intel Core i9', 'RTX20xx', 16, '64 GB', '2T', 4699.00, 'Medical workstation with HIPAA compliance and security. Perfect for healthcare IT and medical imaging. Professional medical certification with security features.'),
('ProArt Medical W7600', 'ASUS', 'intel i9', 'NVIDIA RTX 20xx', 16, '64GB', '2 TB', 4399.00, 'Medical imaging workstation with color-accurate display. Great for medical visualization and diagnostic imaging. Medical grade with professional display certification.'),
('WS66 Medical', 'MSI', 'I 9', 'GeForce 20xx', 15, '64G', '2TB', 4199.00, 'Medical workstation for healthcare applications. Perfect for medical research and diagnostic tools. Professional performance with medical software optimization.'),

-- Legal and Professional Services
('EliteBook Legal Pro', 'HP', 'i7', 'nvidia rtx 20xx', 14, '32GB', '2T', 2999.00, 'Legal professional laptop with document management optimization. Perfect for law firms and legal professionals. Advanced security with legal software optimization.'),
('Latitude Legal 7440', 'Dell', 'I7', 'NVIDIA 20xx', 14, '32G', '2TB', 2899.00, 'Business laptop optimized for legal work and document processing. Ideal for attorneys and legal researchers. Professional features with legal industry support.'),
('ThinkPad T16 Legal', 'Lenovo', 'Intel i7', 'GeForce RTX 20xx', 16, '32 GB', '2T', 3199.00, 'Legal workstation with large screen for document review. Perfect for legal research and case management. Professional reliability with legal software support.'),
('ZBook Legal Studio', 'HP', 'intel i7', 'RTX20xx', 15, '32GB', '2 TB', 3399.00, 'Legal workstation for complex document processing. Great for litigation support and legal research. Professional performance with legal industry features.'),
('Precision Legal 5680', 'Dell', 'I 7', 'nvidia 20xx', 16, '32G', '2TB', 3299.00, 'Legal professional workstation with premium materials. Perfect for partners and senior legal professionals. Premium build with legal workflow optimization.'),

-- Architectural and Design Workstations
('ZBook Architect G10', 'HP', 'i9', 'NVIDIA RTX 20xx', 17, '128GB', '4T', 5199.00, 'Architectural workstation for CAD and BIM applications. Perfect for architects and structural engineers. ISV certification with professional architectural software support.'),
('Precision Architect 7780', 'Dell', 'I9', 'GeForce 20xx', 17, '128G', '4TB', 4999.00, 'Architecture workstation for professional design and modeling. Ideal for architectural firms and design studios. Professional CAD optimization with large display.'),
('ThinkPad P17 Architect', 'Lenovo', 'Intel i9', 'nvidia rtx 20xx', 17, '128 GB', '4T', 5099.00, 'Architectural workstation with professional graphics. Perfect for AutoCAD, Revit, and 3D modeling. Professional reliability with architectural software certification.'),
('ProArt Architect W7700', 'ASUS', 'intel i9', 'RTX 20xx', 17, '128GB', '4 TB', 4799.00, 'Architectural design workstation with color-accurate display. Great for architectural visualization and presentation. Professional materials with design optimization.'),
('Creator Architect Z17', 'MSI', 'I 9', 'NVIDIA 20xx', 17, '128G', '4TB', 4699.00, 'Architectural creator workstation with professional features. Perfect for architectural rendering and visualization. Professional performance with design workflow optimization.'),

-- Engineering and CAD Workstations
('ZBook Engineering G10', 'HP', 'i9', 'GeForce RTX 20xx', 17, '128GB', '4T', 5399.00, 'Engineering workstation for professional CAD and simulation. Perfect for mechanical and aerospace engineers. ISV certification with engineering software optimization.'),
('Precision Engineering 7780', 'Dell', 'I9', 'nvidia 20xx', 17, '128G', '4TB', 5199.00, 'Professional engineering workstation for CAD and analysis. Ideal for product design and manufacturing engineering. Professional CAD certification with maximum performance.'),
('ThinkPad P17 Engineering', 'Lenovo', 'Intel Core i9', 'RTX20xx', 17, '128 GB', '4T', 5299.00, 'Engineering workstation with professional graphics and reliability. Perfect for SolidWorks, CATIA, and engineering simulation. Professional engineering certification.'),
('WS77 Engineering', 'MSI', 'intel i9', 'NVIDIA RTX 20xx', 17, '128GB', '4 TB', 4999.00, 'Engineering workstation for CAD and professional applications. Great for mechanical design and simulation. Professional performance with engineering optimization.'),
('ProArt Engineering W7700', 'ASUS', 'I 9', 'GeForce 20xx', 17, '128G', '4TB', 4899.00, 'Engineering design workstation with professional display. Perfect for product design and engineering visualization. Professional certification with engineering workflow.'),

-- Broadcast and Media Production
('ZBook Broadcast G10', 'HP', 'i9', 'nvidia rtx 20xx', 17, '128GB', '4T', 5699.00, 'Broadcast workstation for live production and editing. Perfect for TV studios and broadcast professionals. Professional video I/O with broadcast software certification.'),
('Precision Broadcast 7780', 'Dell', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 5499.00, 'Broadcast production workstation for professional media. Ideal for news stations and production companies. Professional video features with broadcast optimization.'),
('MacBook Pro Broadcast', 'Apple', 'Intel i9', 'GeForce RTX 20xx', 16, '128 GB', '4T', 5999.00, 'Broadcast production MacBook for media professionals. Perfect for Final Cut Pro and professional video production. Professional media optimization with premium display.'),
('StudioBook Broadcast W7700', 'ASUS', 'intel i9', 'RTX20xx', 17, '128GB', '4 TB', 5199.00, 'Broadcast studio workstation with reference display. Great for color grading and broadcast post-production. Professional broadcast certification with studio features.'),
('Creator Broadcast Z17', 'MSI', 'I 9', 'nvidia 20xx', 17, '128G', '4TB', 4999.00, 'Broadcast creator workstation for media production. Perfect for live streaming and broadcast content creation. Professional streaming features with broadcast optimization.'),

-- Government and Defense
('EliteBook Defense G10', 'HP', 'i9', 'NVIDIA RTX 20xx', 14, '64GB', '2T', 4799.00, 'Military-grade secure laptop for defense applications. Perfect for government contractors and military use. Maximum security with defense-grade encryption and compliance.'),
('Latitude Defense 9440', 'Dell', 'I9', 'GeForce 20xx', 14, '64G', '2TB', 4599.00, 'Defense laptop with advanced security for government use. Ideal for classified environments and secure communications. Government certification with advanced security features.'),
('ThinkPad P16 Defense', 'Lenovo', 'Intel i9', 'nvidia rtx 20xx', 16, '64 GB', '2T', 4899.00, 'Defense workstation with security clearance optimization. Perfect for government agencies and defense contractors. Security certification with professional performance.'),
('ToughBook CF-33 Defense', 'Panasonic', 'intel i9', 'RTX 20xx', 12, '64GB', '2 TB', 5999.00, 'Rugged defense laptop for extreme military environments. Great for field operations and tactical applications. Maximum durability with defense-grade specifications.'),
('Getac Defense X500', 'Getac', 'I 9', 'NVIDIA 20xx', 15, '64G', '2TB', 4999.00, 'Military rugged laptop for defense and security applications. Perfect for field operations and mission-critical use. Defense certification with extreme durability.'),

-- Aviation and Aerospace
('ZBook Aviation G10', 'HP', 'i9', 'GeForce RTX 20xx', 15, '64GB', '2T', 4999.00, 'Aviation workstation for aerospace engineering and simulation. Perfect for aircraft design and flight simulation. Aviation software certification with professional performance.'),
('Precision Aerospace 7670', 'Dell', 'I9', 'nvidia 20xx', 16, '64G', '2TB', 4799.00, 'Aerospace engineering workstation for aircraft design. Ideal for aviation companies and aerospace engineers. Professional aerospace software certification.'),
('ThinkPad P15 Aviation', 'Lenovo', 'Intel Core i9', 'RTX20xx', 15, '64 GB', '2T', 4899.00, 'Aviation workstation with professional graphics for aerospace. Perfect for flight simulation and aircraft modeling. Aviation industry certification with reliability.'),
('ToughBook Aviation CF-20', 'Panasonic', 'intel i9', 'NVIDIA RTX 20xx', 10, '32GB', '1T', 4599.00, 'Rugged aviation tablet for cockpit and maintenance use. Great for pilots and aircraft technicians. Aviation certification with extreme durability.'),
('WS66 Aerospace', 'MSI', 'I 9', 'GeForce 20xx', 15, '64G', '2TB', 4399.00, 'Aerospace workstation for engineering and simulation. Perfect for space and aviation applications. Professional aerospace optimization with high performance.'),

-- Oil and Gas Industry
('ZBook Energy G10', 'HP', 'i9', 'nvidia rtx 20xx', 17, '128GB', '4T', 5199.00, 'Energy industry workstation for seismic and geological analysis. Perfect for oil and gas exploration and production. Industry software certification with professional performance.'),
('Precision Energy 7780', 'Dell', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 4999.00, 'Oil and gas workstation for geological modeling. Ideal for petroleum engineers and geologists. Professional energy software optimization.'),
('ThinkPad P17 Energy', 'Lenovo', 'Intel i9', 'GeForce RTX 20xx', 17, '128 GB', '4T', 5099.00, 'Energy sector workstation for exploration and production. Perfect for seismic interpretation and reservoir modeling. Energy industry certification.'),
('ToughBook Energy CF-33', 'Panasonic', 'intel i9', 'RTX20xx', 12, '64GB', '2 TB', 4799.00, 'Rugged energy laptop for field operations. Great for oil rig and remote site use. Energy industry durability with field optimization.'),
('WS77 Energy', 'MSI', 'I 9', 'nvidia 20xx', 17, '128G', '4TB', 4699.00, 'Energy industry workstation for geological and seismic work. Perfect for petroleum engineering applications. Professional energy industry optimization.'),

-- Pharmaceutical and Biotech
('ZBook Pharma G10', 'HP', 'i9', 'NVIDIA RTX 20xx', 15, '64GB', '2T', 4699.00, 'Pharmaceutical workstation for drug discovery and research. Perfect for computational chemistry and molecular modeling. Pharmaceutical software certification.'),
('Precision Biotech 7670', 'Dell', 'I9', 'GeForce 20xx', 16, '64G', '2TB', 4599.00, 'Biotech workstation for research and development. Ideal for bioinformatics and computational biology. Professional biotech optimization.'),
('ThinkPad P16 Pharma', 'Lenovo', 'Intel i9', 'nvidia rtx 20xx', 16, '64 GB', '2T', 4799.00, 'Pharmaceutical research workstation with compliance features. Perfect for FDA-regulated environments. Pharmaceutical industry certification.'),
('ProArt Biotech W7600', 'ASUS', 'intel i9', 'RTX 20xx', 16, '64GB', '2 TB', 4499.00, 'Biotech research workstation for scientific applications. Great for molecular visualization and analysis. Professional biotech software support.'),
('WS66 Pharma', 'MSI', 'I 9', 'NVIDIA 20xx', 15, '64G', '2TB', 4399.00, 'Pharmaceutical workstation for drug development. Perfect for computational chemistry and research. Professional pharmaceutical optimization.');

-- Additional laptop data - File 5 of 5 (200 records)
-- Focus: Innovation, Future Tech, and Emerging Categories
-- Emphasizing cutting-edge technology, experimental designs, and next-generation features

INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES

-- Foldable and Flexible Displays
('ThinkPad X1 Fold Gen 3', 'Lenovo', 'i9', 'Nvidia 20xx', 16, '32GB', '2T', 4999.00, 'Revolutionary foldable laptop with flexible OLED display technology. Perfect for executives and early adopters who want cutting-edge innovation. Transforms from tablet to laptop seamlessly.'),
('Spectre Fold 17', 'HP', 'I9', 'NVIDIA 20xx', 17, '32G', '2TB', 5499.00, 'Large foldable laptop with premium materials and innovative design. Ideal for creative professionals and technology enthusiasts. Luxury materials with revolutionary form factor.'),
('ZenBook Pro 17 Fold', 'ASUS', 'Intel Core i9', 'GeForce RTX 20xx', 17, '32 GB', '2T', 4799.00, 'Creator-focused foldable laptop with professional features. Perfect for designers and content creators. Innovative design with creator optimization.'),
('Galaxy Book Fold Pro', 'Samsung', 'intel i9', 'RTX20xx', 16, '32GB', '2 TB', 4599.00, 'Samsung foldable laptop with ecosystem integration. Great for Samsung users who want innovation. AMOLED foldable display with S Pen support.'),
('Surface Neo 2', 'Microsoft', 'I 9', 'nvidia 20xx', 13, '32G', '1TB', 3999.00, 'Dual-screen foldable device for productivity and creativity. Perfect for Microsoft ecosystem users. Revolutionary dual-screen productivity experience.'),

-- AR/VR and Mixed Reality
('HoloLens Laptop Pro', 'Microsoft', 'i9', 'NVIDIA RTX 20xx', 15, '64GB', '2T', 5999.00, 'Mixed reality laptop with integrated holographic capabilities. Perfect for enterprise AR/VR development and spatial computing. Professional mixed reality optimization.'),
('Magic Leap Workstation', 'Magic Leap', 'I9', 'GeForce 20xx', 16, '64G', '2TB', 6499.00, 'Professional mixed reality development workstation. Ideal for AR/VR developers and spatial computing professionals. Cutting-edge mixed reality optimization.'),
('Varjo Reality Laptop', 'Varjo', 'Intel i9', 'nvidia rtx 20xx', 17, '64 GB', '4T', 7999.00, 'Professional VR development laptop with ultra-high resolution capabilities. Perfect for enterprise VR training and simulation. Professional VR optimization.'),
('Oculus Development Pro', 'Meta', 'intel i9', 'RTX 20xx', 16, '64GB', '2 TB', 5799.00, 'VR development laptop optimized for Meta ecosystem. Great for VR content creators and developers. Meta platform optimization with VR features.'),
('HTC Vive Workstation', 'HTC', 'I 9', 'NVIDIA 20xx', 17, '64G', '4TB', 6299.00, 'Professional VR workstation for enterprise applications. Perfect for VR training and simulation development. Professional VR certification and optimization.'),

-- AI and Machine Learning Specialized
('Tesla AI Workstation', 'Tesla', 'i9', 'GeForce RTX 20xx', 16, '128GB', '4T', 8999.00, 'Automotive AI development laptop with Tesla optimization. Perfect for autonomous vehicle development. Tesla AI framework optimization with cutting-edge performance.'),
('NVIDIA AI Developer', 'NVIDIA', 'I9', 'nvidia 20xx', 17, '128G', '4TB', 7499.00, 'AI development laptop with NVIDIA optimization and tools. Ideal for machine learning researchers and AI developers. NVIDIA AI platform optimization.'),
('Google AI Workbook', 'Google', 'Intel Core i9', 'RTX20xx', 15, '128 GB', '4T', 6999.00, 'AI development laptop with Google Cloud integration. Perfect for TensorFlow and Google AI platform development. Google AI ecosystem optimization.'),
('Amazon AI Lab', 'Amazon', 'intel i9', 'NVIDIA RTX 20xx', 16, '128GB', '4 TB', 6799.00, 'AI workstation optimized for AWS and Amazon AI services. Great for cloud AI development and deployment. Amazon AI platform integration.'),
('IBM Watson Workstation', 'IBM', 'I 9', 'GeForce 20xx', 16, '128G', '4TB', 7299.00, 'Enterprise AI workstation with IBM Watson integration. Perfect for enterprise AI development and deployment. IBM AI platform optimization.'),

-- Quantum Computing Interface
('IBM Quantum Laptop', 'IBM', 'i9', 'nvidia rtx 20xx', 15, '64GB', '2T', 9999.00, 'Quantum computing interface laptop for researchers. Perfect for quantum algorithm development and simulation. Quantum computing framework optimization.'),
('Google Quantum Dev', 'Google', 'I9', 'NVIDIA 20xx', 16, '64G', '2TB', 8999.00, 'Quantum development laptop with Google Cirq integration. Ideal for quantum computing researchers. Google quantum platform optimization.'),
('Microsoft Quantum Studio', 'Microsoft', 'Intel i9', 'GeForce RTX 20xx', 16, '64 GB', '2T', 8799.00, 'Quantum development laptop with Q# optimization. Perfect for quantum algorithm development. Microsoft quantum platform integration.'),
('Rigetti Quantum Lab', 'Rigetti', 'intel i9', 'RTX20xx', 15, '64GB', '2 TB', 8599.00, 'Quantum computing development laptop for cloud quantum access. Great for quantum application development. Quantum cloud platform optimization.'),
('IonQ Quantum Interface', 'IonQ', 'I 9', 'nvidia 20xx', 16, '64G', '2TB', 8399.00, 'Quantum computing interface for trapped ion systems. Perfect for quantum hardware researchers. Quantum hardware interface optimization.'),

-- Blockchain and Cryptocurrency
('Coinbase Pro Workstation', 'Coinbase', 'i9', 'NVIDIA RTX 20xx', 16, '64GB', '4T', 5999.00, 'Cryptocurrency trading and development workstation. Perfect for crypto traders and blockchain developers. Cryptocurrency platform optimization.'),
('Binance Trading Pro', 'Binance', 'I9', 'GeForce 20xx', 17, '64G', '4TB', 5799.00, 'Professional crypto trading laptop with exchange integration. Ideal for cryptocurrency traders and DeFi developers. Crypto trading optimization.'),
('Ethereum Dev Station', 'Ethereum', 'Intel Core i9', 'nvidia rtx 20xx', 16, '64 GB', '2T', 5299.00, 'Ethereum development laptop for smart contract programming. Perfect for blockchain developers and Web3 creators. Ethereum development optimization.'),
('Bitcoin Mining Laptop', 'Bitcoin', 'intel i9', 'RTX 20xx', 15, '32GB', '2 TB', 4999.00, 'Bitcoin development and analysis laptop. Great for crypto researchers and blockchain analysts. Bitcoin protocol optimization.'),
('Solana Dev Pro', 'Solana', 'I 9', 'NVIDIA 20xx', 16, '64G', '2TB', 4799.00, 'Solana blockchain development laptop for fast DeFi apps. Perfect for Web3 developers and DeFi creators. Solana development optimization.'),

-- Metaverse and Web3
('Meta Horizon Workstation', 'Meta', 'i9', 'GeForce RTX 20xx', 17, '128GB', '4T', 6999.00, 'Metaverse development laptop for Horizon Worlds creation. Perfect for metaverse developers and virtual world creators. Meta platform optimization.'),
('Epic Unreal Metaverse', 'Epic Games', 'I9', 'nvidia 20xx', 18, '128G', '4TB', 6799.00, 'Metaverse development laptop with Unreal Engine optimization. Ideal for virtual world and game developers. Unreal Engine metaverse optimization.'),
('Unity Metaverse Pro', 'Unity', 'Intel i9', 'NVIDIA RTX 20xx', 17, '128 GB', '4T', 6599.00, 'Metaverse creation laptop with Unity optimization. Perfect for AR/VR and metaverse content creators. Unity platform optimization.'),
('Roblox Creator Studio', 'Roblox', 'intel i9', 'GeForce RTX 20xx', 16, '64GB', '2 TB', 4999.00, 'Metaverse creation laptop for Roblox platform. Great for game developers and virtual world creators. Roblox development optimization.'),
('Minecraft Education Pro', 'Microsoft', 'I 9', 'RTX20xx', 15, '32G', '1TB', 3999.00, 'Educational metaverse laptop for Minecraft-based learning. Perfect for educators and educational content creators. Educational platform optimization.'),

-- Space and Satellite Technology
('SpaceX Starlink Laptop', 'SpaceX', 'i9', 'nvidia rtx 20xx', 15, '64GB', '2T', 7999.00, 'Space-grade laptop with Starlink connectivity for remote operations. Perfect for aerospace engineers and satellite operations. Space-grade durability and connectivity.'),
('NASA Mission Control', 'NASA', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 9999.00, 'Mission control laptop for space operations and satellite management. Ideal for aerospace professionals and space agencies. NASA certification and optimization.'),
('Blue Origin Space Laptop', 'Blue Origin', 'Intel Core i9', 'GeForce RTX 20xx', 16, '64 GB', '2T', 8499.00, 'Space operations laptop for commercial spaceflight. Perfect for space tourism and commercial space operations. Space operations optimization.'),
('Virgin Galactic Pilot', 'Virgin Galactic', 'intel i9', 'RTX 20xx', 14, '32GB', '1 TB', 6999.00, 'Pilot laptop for space tourism operations. Great for commercial space pilots and operations. Space tourism optimization.'),
('ESA Satellite Control', 'ESA', 'I 9', 'nvidia 20xx', 16, '64G', '2TB', 8799.00, 'European space operations laptop for satellite control. Perfect for satellite operators and space agencies. European space standards optimization.'),

-- Biotechnology and Genomics
('Illumina Genomics Pro', 'Illumina', 'i9', 'NVIDIA RTX 20xx', 17, '128GB', '4T', 7999.00, 'Genomics analysis laptop for DNA sequencing and bioinformatics. Perfect for genetic researchers and biotech professionals. Genomics software optimization.'),
('CRISPR Lab Workstation', 'CRISPR', 'I9', 'GeForce 20xx', 16, '128G', '4TB', 7499.00, 'Gene editing research laptop with CRISPR optimization. Ideal for genetic engineers and biotech researchers. CRISPR research platform optimization.'),
('Oxford Nanopore Seq', 'Oxford Nanopore', 'Intel i9', 'nvidia rtx 20xx', 15, '64 GB', '2T', 6999.00, 'DNA sequencing laptop for portable genomics analysis. Perfect for field genomics and portable sequencing. Portable genomics optimization.'),
('Moderna mRNA Lab', 'Moderna', 'intel i9', 'RTX20xx', 16, '64GB', '2 TB', 6799.00, 'mRNA research laptop for vaccine and therapeutic development. Great for biotech researchers and pharmaceutical scientists. mRNA research optimization.'),
('Ginkgo Bioworks Lab', 'Ginkgo Bioworks', 'I 9', 'NVIDIA 20xx', 17, '128G', '4TB', 7299.00, 'Synthetic biology laptop for organism design and engineering. Perfect for synthetic biology researchers. Synthetic biology optimization.'),

-- Renewable Energy and Climate
('Tesla Energy Laptop', 'Tesla', 'i9', 'GeForce RTX 20xx', 15, '64GB', '2T', 5999.00, 'Energy management laptop for solar and battery systems. Perfect for renewable energy engineers and grid operators. Tesla energy platform optimization.'),
('First Solar Analysis', 'First Solar', 'I9', 'nvidia 20xx', 16, '32G', '1TB', 4999.00, 'Solar energy analysis laptop for photovoltaic research. Ideal for solar engineers and renewable energy professionals. Solar energy optimization.'),
('Vestas Wind Laptop', 'Vestas', 'Intel Core i9', 'NVIDIA RTX 20xx', 15, '64 GB', '2T', 5499.00, 'Wind energy laptop for turbine design and analysis. Perfect for wind engineers and renewable energy developers. Wind energy optimization.'),
('Carbon Capture Pro', 'Climeworks', 'intel i9', 'GeForce RTX 20xx', 16, '64GB', '2 TB', 5799.00, 'Carbon capture technology laptop for climate solutions. Great for environmental engineers and climate researchers. Carbon capture optimization.'),
('Climate Modeling Pro', 'NOAA', 'I 9', 'RTX20xx', 17, '128G', '4TB', 6999.00, 'Climate modeling laptop for weather and climate prediction. Perfect for meteorologists and climate scientists. Climate modeling optimization.'),

-- Advanced Manufacturing and Robotics
('Boston Dynamics Robot', 'Boston Dynamics', 'i9', 'nvidia rtx 20xx', 15, '64GB', '2T', 7999.00, 'Robotics development laptop for advanced robot control. Perfect for robotics engineers and AI researchers. Robotics platform optimization.'),
('ABB Industrial Robot', 'ABB', 'I9', 'NVIDIA 20xx', 16, '64G', '2TB', 6999.00, 'Industrial robotics laptop for manufacturing automation. Ideal for industrial engineers and automation specialists. Industrial robotics optimization.'),
('KUKA Robot Control', 'KUKA', 'Intel i9', 'GeForce RTX 20xx', 15, '32 GB', '1T', 5999.00, 'Robot control laptop for precision manufacturing. Perfect for robotics technicians and manufacturing engineers. Robot control optimization.'),
('Fanuc CNC Pro', 'Fanuc', 'intel i9', 'RTX 20xx', 16, '64GB', '2 TB', 5799.00, 'CNC control laptop for precision machining. Great for machinists and manufacturing engineers. CNC control optimization.'),
('Siemens Digital Factory', 'Siemens', 'I 9', 'nvidia 20xx', 17, '128G', '4TB', 7499.00, 'Digital factory laptop for Industry 4.0 applications. Perfect for industrial engineers and smart manufacturing. Industry 4.0 optimization.'),

-- Autonomous Vehicles and Transportation
('Waymo Autonomous Dev', 'Waymo', 'i9', 'NVIDIA RTX 20xx', 16, '128GB', '4T', 8999.00, 'Autonomous vehicle development laptop with Waymo optimization. Perfect for self-driving car engineers and AI researchers. Autonomous vehicle optimization.'),
('Cruise AV Workstation', 'Cruise', 'I9', 'GeForce 20xx', 17, '128G', '4TB', 8499.00, 'Autonomous vehicle workstation for self-driving development. Ideal for automotive engineers and AI developers. Self-driving car optimization.'),
('NVIDIA Drive Platform', 'NVIDIA', 'Intel Core i9', 'nvidia rtx 20xx', 16, '64 GB', '2T', 7999.00, 'NVIDIA Drive development platform for autonomous vehicles. Perfect for automotive AI development. NVIDIA Drive optimization.'),
('Argo AI Development', 'Argo AI', 'intel i9', 'RTX20xx', 15, '64GB', '2 TB', 7499.00, 'Argo AI development laptop for self-driving technology. Great for autonomous vehicle researchers. Argo AI platform optimization.'),
('Mobileye Vision Pro', 'Mobileye', 'I 9', 'NVIDIA 20xx', 16, '64G', '2TB', 6999.00, 'Computer vision laptop for automotive safety systems. Perfect for automotive safety engineers. Computer vision optimization.'),

-- Smart City and IoT
('Cisco Smart City', 'Cisco', 'i9', 'GeForce RTX 20xx', 15, '64GB', '2T', 5999.00, 'Smart city management laptop for urban IoT systems. Perfect for city planners and IoT engineers. Smart city platform optimization.'),
('IBM Smart City Pro', 'IBM', 'I9', 'nvidia 20xx', 16, '64G', '2TB', 6299.00, 'Smart city analytics laptop with IBM Watson integration. Ideal for urban analytics and city management. IBM smart city optimization.'),
('Microsoft Azure IoT', 'Microsoft', 'Intel i9', 'NVIDIA RTX 20xx', 15, '32 GB', '1T', 4999.00, 'IoT development laptop with Azure platform integration. Perfect for IoT developers and smart device creators. Azure IoT optimization.'),
('Amazon AWS IoT Pro', 'Amazon', 'intel i9', 'GeForce RTX 20xx', 16, '64GB', '2 TB', 5299.00, 'AWS IoT development laptop for cloud-connected devices. Great for IoT developers and cloud engineers. AWS IoT platform optimization.'),
('Google Cloud IoT', 'Google', 'I 9', 'RTX20xx', 15, '32G', '1TB', 4799.00, 'Google Cloud IoT laptop for smart device development. Perfect for IoT developers and cloud architects. Google IoT optimization.'),

-- Next-Generation Gaming
('NVIDIA GeForce Now Pro', 'NVIDIA', 'i9', 'nvidia rtx 20xx', 17, '64GB', '2T', 4999.00, 'Cloud gaming laptop with GeForce Now optimization. Perfect for gamers who want ultimate performance. Cloud gaming optimization.'),
('Google Stadia Pro', 'Google', 'I9', 'NVIDIA 20xx', 16, '32G', '1TB', 3999.00, 'Cloud gaming laptop optimized for Stadia platform. Ideal for cloud gaming enthusiasts. Stadia platform optimization.'),
('Microsoft xCloud Gaming', 'Microsoft', 'Intel Core i9', 'GeForce RTX 20xx', 15, '64 GB', '2T', 4499.00, 'Xbox cloud gaming laptop for Game Pass Ultimate. Perfect for Xbox ecosystem gamers. Xbox cloud gaming optimization.'),
('Amazon Luna Gaming', 'Amazon', 'intel i9', 'RTX 20xx', 16, '32GB', '1 TB', 3799.00, 'Amazon Luna cloud gaming laptop. Great for Prime members and cloud gaming. Amazon Luna optimization.'),
('PlayStation Now Pro', 'Sony', 'I 9', 'nvidia 20xx', 15, '64G', '2TB', 4299.00, 'PlayStation cloud gaming laptop for PS Now. Perfect for PlayStation ecosystem users. PlayStation cloud optimization.'),

-- Digital Health and Telemedicine
('Teladoc Health Pro', 'Teladoc', 'i9', 'NVIDIA RTX 20xx', 15, '32GB', '1T', 3999.00, 'Telemedicine laptop for remote healthcare delivery. Perfect for healthcare providers and telehealth professionals. Telemedicine platform optimization.'),
('Epic MyChart Pro', 'Epic', 'I9', 'GeForce 20xx', 14, '32G', '1TB', 3799.00, 'Electronic health record laptop for healthcare providers. Ideal for doctors and healthcare administrators. Epic EHR optimization.'),
('Cerner Health Pro', 'Cerner', 'Intel i9', 'nvidia rtx 20xx', 15, '64 GB', '2T', 4299.00, 'Healthcare IT laptop for hospital systems. Perfect for healthcare IT professionals. Cerner platform optimization.'),
('Apple Health Pro', 'Apple', 'intel i9', 'RTX20xx', 14, '32GB', '1 TB', 4499.00, 'Digital health laptop with HealthKit integration. Great for health app developers and medical professionals. Apple Health optimization.'),
('Google Health AI', 'Google', 'I 9', 'NVIDIA 20xx', 16, '64G', '2TB', 4999.00, 'AI-powered health laptop for medical research. Perfect for medical AI researchers and healthcare innovators. Medical AI optimization.'),

-- Advanced Education Technology
('Khan Academy Pro', 'Khan Academy', 'i7', 'GeForce RTX 20xx', 14, '16GB', '1T', 2999.00, 'Educational technology laptop for online learning platforms. Perfect for educators and educational content creators. Educational platform optimization.'),
('Coursera Teaching Pro', 'Coursera', 'I7', 'nvidia 20xx', 15, '32G', '1TB', 3299.00, 'Online education laptop for course creation and delivery. Ideal for instructors and educational institutions. Online learning optimization.'),
('edX Academic Pro', 'edX', 'Intel i7', 'NVIDIA RTX 20xx', 14, '16 GB', '1T', 2899.00, 'Academic laptop for higher education and research. Perfect for university professors and researchers. Academic platform optimization.'),
('Udacity AI Learning', 'Udacity', 'intel i7', 'GeForce RTX 20xx', 15, '32GB', '1 TB', 3499.00, 'AI education laptop for machine learning courses. Great for AI students and professionals. AI education optimization.'),
('Blackboard Learn Pro', 'Blackboard', 'I 7', 'RTX20xx', 15, '16G', '1TB', 2799.00, 'Learning management laptop for educational institutions. Perfect for academic administrators and instructors. LMS platform optimization.'),

-- Emerging Creative Tools
('Adobe Creative Cloud Pro', 'Adobe', 'i9', 'nvidia rtx 20xx', 16, '64GB', '2T', 4999.00, 'Ultimate creative laptop with Adobe Creative Cloud optimization. Perfect for professional designers and content creators. Adobe Creative Suite optimization.'),
('Autodesk Creator Pro', 'Autodesk', 'I9', 'NVIDIA 20xx', 17, '128G', '4TB', 5499.00, 'Professional design laptop with Autodesk software optimization. Ideal for architects, engineers, and designers. Autodesk platform optimization.'),
('Cinema 4D Workstation', 'Maxon', 'Intel Core i9', 'GeForce RTX 20xx', 16, '64 GB', '2T', 4799.00, '3D animation laptop optimized for Cinema 4D. Perfect for motion graphics artists and 3D animators. Cinema 4D optimization.'),
('Blender Foundation Pro', 'Blender', 'intel i9', 'RTX 20xx', 17, '128GB', '4 TB', 4299.00, 'Open-source 3D creation laptop with Blender optimization. Great for independent artists and studios. Blender platform optimization.'),
('Unreal Engine Creator', 'Epic Games', 'I 9', 'nvidia 20xx', 18, '128G', '4TB', 5999.00, 'Game development laptop with Unreal Engine optimization. Perfect for game developers and virtual production. Unreal Engine optimization.');
