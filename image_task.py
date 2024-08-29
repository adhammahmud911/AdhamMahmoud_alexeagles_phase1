#!/usr/bin/env python3
import cv2 as cv
import numpy as np
from helper_functions import filter_contours, classify_contour, evaluate_inner_diameter, get_user_input

if __name__ == '__main__':

    # Loading the ideal and test images and creating blank canvases for drawing contours
    reference_img = cv.imread('./task_images/ideal.jpg')
    test_img = cv.imread('./task_images/sample3.jpg')
    blank_reference = np.zeros(reference_img.shape, dtype='uint8')
    blank_test = np.zeros(reference_img.shape, dtype='uint8')
    blank_difference = np.zeros(reference_img.shape, dtype='uint8')
    inner_diameter_mask_blank = np.zeros(reference_img.shape[:2], dtype='uint8')

    ## Converting images from BGR to Grayscale
    ref_img_gray = cv.cvtColor(reference_img, cv.COLOR_BGR2GRAY)
    test_img_gray = cv.cvtColor(test_img, cv.COLOR_BGR2GRAY)

    # Creating a circular mask centered on the image to isolate the inner diameter
    mask = cv.circle(inner_diameter_mask_blank, (reference_img.shape[1]//2, reference_img.shape[0]//2), 110, 255, -1)
    inverted_mask = cv.bitwise_not(mask)

    masked_ref_img = cv.bitwise_and(ref_img_gray, ref_img_gray, mask=mask)
    masked_test_img = cv.bitwise_and(test_img_gray, test_img_gray, mask=mask)
    inverted_masked_ref_img = cv.bitwise_and(ref_img_gray, ref_img_gray, mask=inverted_mask)
    inverted_masked_test_img = cv.bitwise_and(test_img_gray, test_img_gray, mask=inverted_mask)

    # Evaluating inner diameter condition
    diameter_status, inner_diameter_difference = evaluate_inner_diameter(masked_ref_img, masked_test_img, blank_difference)

    ## Thresholding the reference and test images
    _, threshold_ref = cv.threshold(inverted_masked_ref_img, 90, 255, cv.THRESH_BINARY)
    _, threshold_test = cv.threshold(inverted_masked_test_img, 90, 255, cv.THRESH_BINARY)

    ## Finding differences between the reference and test images using XOR operation
    difference_img = cv.bitwise_xor(threshold_ref, threshold_test)
    overall_difference_img = difference_img.copy()
    if diameter_status != 'Normal':
        overall_difference_img = cv.bitwise_or(difference_img, inner_diameter_difference)

    # Finding contours in the reference, test, and difference images
    contours_ref, _ = cv.findContours(threshold_ref, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours_test, _ = cv.findContours(threshold_test, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    difference_contours, _ = cv.findContours(difference_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # Filtering out small contours (noise)
    significant_diff_contours = filter_contours(difference_contours)

    # Drawing contours on the blank images
    cv.drawContours(blank_reference, contours_ref, -1, (0, 0, 255), 1)
    cv.drawContours(blank_test, contours_test, -1, (0, 0, 255), 1)
    cv.drawContours(blank_difference, significant_diff_contours, -1, (0, 0, 255), 1)

    # Counting worn and missing teeth based on the contours
    worn_teeth_count = 0
    missing_teeth_count = 0
    worn_teeth_count, missing_teeth_count = classify_contour(significant_diff_contours, worn_teeth_count, missing_teeth_count)

    # Displaying the results
    print(f'Number of missing teeth: {missing_teeth_count}')
    print('-------------------')
    print(f'Number of worn teeth: {worn_teeth_count}')
    print('-------------------')
    print(f'The condition of the inner diameter is: {diameter_status}')

    # Display the difference images
    cv.imshow('Overall Difference', overall_difference_img)
    cv.imshow('Significant Difference Contours', blank_difference)
    cv.waitKey(0)
