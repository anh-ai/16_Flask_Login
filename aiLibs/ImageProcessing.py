import cv2
import numpy as np


def imageCompare(image1, image2, CompareThreshold, fresize=True, debug=False):
    # iOK = ['part1/OK/areaLB/img_labels_OK_P10.jpg_areaLB.jpg']
    # iNG = ['part1/NG/areaLB/img_labels_OK_P10.jpg_areaLB.jpg']

    # Đọc hai ảnh cần so sánh

    w, h = image1.shape[1], image1.shape[0]
    if fresize:
        w, h = (image1.shape[1] * 80 // 100, image1.shape[0] * 80 // 100)
        image1 = cv2.resize(image1, (w, h))
    image2 = cv2.resize(image2, (w, h))
    image1_org = image1.copy()
    image2_org = image2.copy()

    # Chuyển đổi ảnh sang độ xám
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Khởi tạo đối tượng SIFT
    sift = cv2.SIFT_create()

    # Tìm các keypoint và descriptors trong ảnh 1 và ảnh 2
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)

    # Khởi tạo matcher
    matcher = cv2.BFMatcher()

    # Tìm các điểm tương ứng giữa ảnh 1 và ảnh 2
    matches = matcher.match(descriptors1, descriptors2)

    # Sắp xếp các điểm tương ứng theo thứ tự khoảng cách tăng dần
    matches = sorted(matches, key=lambda x: x.distance)

    # Lấy tọa độ các điểm keypoint trong ảnh 1 và ảnh 2
    src_points = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_points = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Ánh xạ (map) ảnh 2 lên ảnh 1
    M, mask = cv2.findHomography(dst_points, src_points, cv2.RANSAC, 5.0)

    # Áp dụng phép biến đổi để có được ảnh đã được đăng ký
    registered_image = cv2.warpPerspective(image2, M, (image1.shape[1], image1.shape[0]))

    # Tìm sự khác biệt giữa ảnh đã đăng ký và ảnh 1
    diff = cv2.absdiff(image1, registered_image)

    # Chuyển đổi ảnh khác biệt sang ảnh đen trắng
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Áp dụng phân đoạn để tách riêng các vùng khác biệt
    _, threshold = cv2.threshold(diff_gray, CompareThreshold, 255, cv2.THRESH_BINARY)  # 70 ==> 30..100

    # Tìm các đối tượng khác biệt trong ảnh nhị phân
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Vẽ hình chữ nhật bao quanh các đối tượng khác biệt
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        # cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.rectangle(registered_image, (x, y), (x + w, y + h), (0, 255, 0), 1)

    if debug:
        # Hiển thị hai ảnh để so sánh
        cv2.imshow("Image 1-Org", image1_org)
        cv2.imshow("Image 2-Org", image2_org)
        cv2.imshow("Image 1", image1)
        cv2.imshow("Registered Image 2", registered_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print('Da xu ly xong')
    mess = f"{len(contours)}: Number of different positions between 2 pictures"
    return image1, registered_image, mess
