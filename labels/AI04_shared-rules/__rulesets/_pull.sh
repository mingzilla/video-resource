#!/bin/bash

function sync_rulesets_directory() {
    PRIMARY_RULESETS_PATH="/mnt/e/code/github-release/video-resource/labels/AI04_shared-rules/__rulesets"
    PROJECT_DIR="$(pwd)"
    RULESETS_TARGET_DIR="$PROJECT_DIR/__rulesets"
    
    # Use the primary rulesets location
    if [[ ! -d "$PRIMARY_RULESETS_PATH" ]]; then
        echo "Error: Cannot find source rulesets directory at $PRIMARY_RULESETS_PATH"
        exit 1
    fi
    
    echo "Copying rulesets - clear existing and copy"
    echo "From: $PRIMARY_RULESETS_PATH"
    echo "To  : $PROJECT_DIR"
    
    if [[ -d "$RULESETS_TARGET_DIR" ]]; then
        rm -rf "$RULESETS_TARGET_DIR"
    fi
    
    cp -r "$PRIMARY_RULESETS_PATH" "$RULESETS_TARGET_DIR"
}

function force_move_file_to_project_root() {
    local filename="$1"
    PROJECT_DIR="$(pwd)"
    RULESETS_TARGET_DIR="$PROJECT_DIR/__rulesets"
    
    # Move file from __rulesets to project root, overwriting current file
    if [[ -f "$RULESETS_TARGET_DIR/$filename" ]]; then
        echo "Move to project root: $filename"
        cp "$RULESETS_TARGET_DIR/$filename" "$PROJECT_DIR/$filename"
        rm "$RULESETS_TARGET_DIR/$filename"
    fi
}

function force_move_files_to_project_root() {
    force_move_file_to_project_root "_pull.sh"
    force_move_file_to_project_root ".gitattributes"
}

function exclude_rulesets_from_gitignore() {
    PROJECT_DIR="$(pwd)"
    GITIGNORE_FILE="$PROJECT_DIR/.gitignore"
    
    # Check if .gitignore exists and add __rulesets if not present
    if [[ -f "$GITIGNORE_FILE" ]]; then
        if ! grep -q "^__rulesets" "$GITIGNORE_FILE"; then
            echo "Adding __rulesets to .gitignore..."
            echo "" >> "$GITIGNORE_FILE"
            echo "__rulesets/" >> "$GITIGNORE_FILE"
        else
            echo "__rulesets already in .gitignore"
        fi
    else
        echo "Creating .gitignore and adding __rulesets..."
        echo "__rulesets/" > "$GITIGNORE_FILE"
    fi
}

# Main execution flow
function main() {
    sync_rulesets_directory
    echo ""
    force_move_files_to_project_root
    echo ""
    exclude_rulesets_from_gitignore
}

# Execute main function
main
