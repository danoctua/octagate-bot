package utils

import (
	"errors"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// Define regular expressions
var contentDispositionFilenameRegex = regexp.MustCompile(`filename="(.+)"`)

// getFilenameFromContentDisposition extracts the filename from the Content-Disposition header
func getFilenameFromContentDisposition(headers http.Header) (string, error) {
	contentDisposition := headers.Get("Content-Disposition")
	if contentDisposition == "" {
		return "", errors.New("Content-Disposition header not found")
	}

	match := contentDispositionFilenameRegex.FindStringSubmatch(contentDisposition)
	if len(match) > 1 {
		return match[1], nil
	}
	return "", errors.New("Filename not found in Content-Disposition header")
}

// guessFileExtension guesses the file extension from the Content-Type header or the Content-Disposition header
func guessFileExtension(resp *http.Response) (string, error) {
	// Try to get from Content-Type header
	contentType := resp.Header.Get("Content-Type")
	if contentType != "" {
		parts := strings.Split(contentType, "/")
		if len(parts) > 1 {
			return parts[len(parts)-1], nil
		}
	}

	// Fallback to Content-Disposition header
	filename, err := getFilenameFromContentDisposition(resp.Header)
	if err == nil && strings.Contains(filename, ".") {
		ext := filepath.Ext(filename)
		if ext != "" {
			return ext[1:], nil // Remove the leading dot
		}
	}

	return "", errors.New("Unable to guess file extension")
}

// downloadMedia downloads a file from the given URL and saves it to the specified path on disk
func DownloadMedia(url, name, subdirectory, defaultExtension string, staticPath string) (string, error) {
	// Ensure default extension starts with a dot
	if !strings.HasPrefix(defaultExtension, ".") {
		defaultExtension = "." + defaultExtension
	}

	// Resolve the full path
	rootPath := staticPath
	if subdirectory != "" {
		rootPath = filepath.Join(staticPath, subdirectory)
	}

	// Create the directories if necessary
	if err := os.MkdirAll(rootPath, os.ModePerm); err != nil {
		return "", err
	}

	// Make the HTTP GET request
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// Guess the file extension
	extension, err := guessFileExtension(resp)
	if err != nil {
		extension = defaultExtension
	}

	// Create the destination file name and path
	fileName := name + extension
	fullPath := filepath.Join(rootPath, fileName)

	// Create and write the file
	file, err := os.Create(fullPath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return "", err
	}

	return fullPath, nil
}

// ImagePreview represents an image preview with a resolution
type ImagePreview struct {
	Resolution string
}

// parseResolution parses a resolution string (e.g., "1920x1080") into width and height
func parseResolution(resolution string) (int, int, error) {
	parts := strings.Split(resolution, "x")
	if len(parts) != 2 {
		return 0, 0, errors.New("Invalid resolution format")
	}

	width, err := strconv.Atoi(parts[0])
	if err != nil {
		return 0, 0, err
	}

	height, err := strconv.Atoi(parts[1])
	if err != nil {
		return 0, 0, err
	}

	return width, height, nil
}

// pickBestPreview selects the best image preview based on its resolution
func PickBestPreview(previews []ImagePreview) (ImagePreview, error) {
	if len(previews) == 0 {
		return ImagePreview{}, errors.New("No previews available")
	}

	sort.Slice(previews, func(i, j int) bool {
		w1, h1, err1 := parseResolution(previews[i].Resolution)
		w2, h2, err2 := parseResolution(previews[j].Resolution)

		if err1 != nil || err2 != nil {
			return false
		}

		return (w1 * h1) < (w2 * h2)
	})

	// Return the best (last after sort)
	return previews[len(previews)-1], nil
}

// cleanOldVersions removes old files in a directory with a specific prefix, excluding the current file
func CleanOldVersions(path, prefix, currentFile string) error {
	files, err := os.ReadDir(path)
	if err != nil {
		return err
	}

	for _, file := range files {
		if strings.HasPrefix(file.Name(), prefix) && file.Name() != currentFile {
			err = os.Remove(filepath.Join(path, file.Name()))
			if err != nil {
				return err
			}
		}
	}

	return nil
}