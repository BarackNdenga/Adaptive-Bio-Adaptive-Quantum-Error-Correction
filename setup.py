from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
      long_description = fh.read()

setup(
      name="bio-adaptive-qec-simulation",
      version="0.1.0",
      author="ChuckGPTX",
      description="Simulation and analysis of a Bio-Adaptive Quantum Error Correction (BA-QEC) decoding strategy",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/ChuckGPTX/bio-adaptive-qec-simulation",
      packages=find_packages(),
      classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Topic :: Scientific/Engineering",
      ],
      python_requires=">=3.8",
      install_requires=[
                "numpy",
                "matplotlib",
                "stim",
                "pymatching",
                "tqdm",
      ],
      extras_require={
                "ibm": ["qiskit", "qiskit-ibm-runtime"],
                "dev": ["pytest", "pytest-cov", "black", "flake8"],
      },
)
