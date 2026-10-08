#include "secblur.hpp"
#include <iostream>

namespace secblur {

    cv::Mat applyObfuscation(const cv::Mat& input_image, const cv::Rect& roi, int kernel_size) {
        cv::Mat result = input_image.clone();
        
        // Ensure the ROI is within the image boundaries
        cv::Rect valid_roi = roi & cv::Rect(0, 0, result.cols, result.rows);
        if (valid_roi.empty()) return result;

        // Apply Gaussian Blur to the selected region
        cv::Mat roi_matrix = result(valid_roi);
        cv::GaussianBlur(roi_matrix, roi_matrix, cv::Size(kernel_size, kernel_size), 0);
        
        return result;
    }

    cv::Mat embedPayload(const cv::Mat& cover_image, const std::string& secret_data) {
        cv::Mat stego_image = cover_image.clone();
        
        // Convert secret string to binary representation
        std::vector<int> binary_data;
        for (char c : secret_data) {
            for (int i = 7; i >= 0; --i) {
                binary_data.push_back((c >> i) & 1);
            }
        }

        // Basic Least Significant Bit (LSB) embedding algorithm
        int data_idx = 0;
        for (int r = 0; r < stego_image.rows && data_idx < binary_data.size(); ++r) {
            for (int c = 0; c < stego_image.cols && data_idx < binary_data.size(); ++c) {
                cv::Vec3b& pixel = stego_image.at<cv::Vec3b>(r, c);
                for (int color = 0; color < 3 && data_idx < binary_data.size(); ++color) {
                    // Clear the LSB and set it to the secret bit
                    pixel[color] = (pixel[color] & ~1) | binary_data[data_idx++];
                }
            }
        }
        return stego_image;
    }

    std::string extractPayload(const cv::Mat& stego_image, size_t data_length) {
        std::string extracted_data = "";
        int bit_count = 0;
        char current_char = 0;
        size_t total_bits = data_length * 8;

        // LSB Extraction algorithm
        for (int r = 0; r < stego_image.rows && bit_count < total_bits; ++r) {
            for (int c = 0; c < stego_image.cols && bit_count < total_bits; ++c) {
                cv::Vec3b pixel = stego_image.at<cv::Vec3b>(r, c);
                for (int color = 0; color < 3 && bit_count < total_bits; ++color) {
                    current_char = (current_char << 1) | (pixel[color] & 1);
                    bit_count++;
                    
                    if (bit_count % 8 == 0) {
                        extracted_data += current_char;
                        current_char = 0;
                    }
                }
            }
        }
        return extracted_data;
    }

    cv::Mat restoreImage(const cv::Mat& blurred_image, const cv::Mat& original_roi_pixels, const cv::Rect& roi) {
        cv::Mat result = blurred_image.clone();
        cv::Rect valid_roi = roi & cv::Rect(0, 0, result.cols, result.rows);
        
        // Replace the blurred region with the original extracted pixels
        if (!valid_roi.empty() && original_roi_pixels.size() == valid_roi.size()) {
            original_roi_pixels.copyTo(result(valid_roi));
        }
        return result;
    }

} // namespace secblur
