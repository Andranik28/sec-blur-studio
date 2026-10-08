#include "secblur.hpp"
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cout << "Usage: ./secblur_cli <input_image_path> <output_image_path>\n";
        return -1;
    }

    std::string input_path = argv[1];
    std::string output_path = argv[2];

    // 1. Read the input image
    cv::Mat image = cv::imread(input_path, cv::IMREAD_COLOR);
    if (image.empty()) {
        std::cerr << "Error: Could not read image at " << input_path << "\n";
        return -1;
    }

    // 2. Define a Region of Interest (e.g., a face bounding box)
    cv::Rect face_roi(100, 100, 150, 150); // X, Y, Width, Height

    // 3. Apply obfuscation (blurring)
    cv::Mat blurred_image = secblur::applyObfuscation(image, face_roi, 31);

    // 4. Embed a dummy restoration payload
    std::string secret_payload = "ENCRYPTED_PIXEL_DATA_PAYLOAD";
    cv::Mat stego_image = secblur::embedPayload(blurred_image, secret_payload);

    // 5. Save the result
    cv::imwrite(output_path, stego_image);
    std::cout << "Successfully generated stego-blurred image: " << output_path << "\n";

    return 0;
}
