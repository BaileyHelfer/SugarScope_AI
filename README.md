# SugarScope AI - Machine Learning Project
![](resources/read_me_preview.PNG?raw=true)

# Background
SugarScope AI is a Machine Learning application that allows you to get real time image classification predictions!

This application uses Microsoft's Lobe backend to make inferences uses a Lobe trained model converted into onnx format. The image input is taken from any camera that supports RTSP Streaming.

# How to use
SugarScope AI comes with a config.yaml file which is where all of your input data will come from. In here you can find the path to your .onnx model file as well as the link to connect to your RTSP camera.

Once your config.yaml file is setup properly you can then connect to your camera and begin your live predictions!
