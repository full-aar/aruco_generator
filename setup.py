from setuptools import setup

setup(
  name = "aruco_generator",
  version = "0.1",
  description = "generate aruco markers",
  url = "",
  author = "miranda",
  author_email = "miranda@pulusound.fi",
  packages = ["aruco_generator"],
  entry_points = {
    "console_scripts": [
      "aruco_generator = aruco_generator:main"
    ]
  },
  install_requires = [
    # we dont list opencv here, as the pip package's name is incompatible with that of the conda package. instead just check for cv2 at runtime
  ],
)
