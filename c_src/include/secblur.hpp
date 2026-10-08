#pragma once
#include <opencv2/opencv.hpp>
#include <string>
#include <vector>

namespace secblur {

    /**
     * @brief Blurs a specific Region of Interest (ROI) in an image.
     * 
     * @param input_image The original image matrix.
     * @param roi The rectangular region to apply the blur.
     * @param kernel_size The size of the Gaussian blur kernel.
     * @return cv::Mat The image with the blurred ROI.
     */
    cv::Mat applyObfuscation(const cv::Mat& input_image, const cv::Rect& roi, int kernel_size = 21);

    /**
     * @brief Embeds secret data (e.g., restoration payload) into the image using LSB Steganography.
     * 
     * @param cover_image The image to hide data inside.
     * @param secret_data A string representing the encrypted/compressed payload.
     * @return cv::Mat The stego-image containing the hidden data.
     */
    cv::Mat embedPayload(const cv::Mat& cover_image, const std::string& secret_data);

    /**
     * @brief Extracts secret data from a stego-image.
     * 
     * @param stego_image The image containing hidden data.
     * @param data_length The expected length of the extracted data.
     * @return std::string The extracted secret payload.
     */
    std::string extractPayload(const cv::Mat& stego_image, size_t data_length);

    /**
     * @brief Restores the original image by replacing the blurred ROI with extracted original pixels.
     * 
     * @param blurred_image The image containing the obfuscated region.
     * @param original_roi_pixels The decrypted original pixels of the ROI.
     * @param roi The rectangular region where the original pixels should be placed.
     * @return cv::Mat The fully restored image.
     */
    cv::Mat restoreImage(const cv::Mat& blurred_image, const cv::Mat& original_roi_pixels, const cv::Rect& roi);

} // namespace secblur
