import cv2


# 输入和输出文件路徑
input_file = 'huh.mp4'
output_file = 'huh.Mjpeg'

# 打開输入影片文件
cap = cv2.VideoCapture(input_file)

if not cap.isOpened():
    print(f"無法打開輸入文件 {input_file}")
    exit()

# 獲取影片的宽度、高度和帧率
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# 假查影片属性是否讀取成功
if frame_width == 0 or frame_height == 0 or fps == 0:
    print("無法讀取影片属性")
    cap.release()
    exit()

# 定义 MJPEG 编码和创建 VideoWriter 对象
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

if not out.isOpened():
    print(f"無法建立输出文件 {output_file}")
    cap.release()
    exit()

# 逐帧读取视频并写入输出文件
while True:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)

# 释放资源
cap.release()
out.release()

print(f"轉換完成，输出文件為 {output_file}")
