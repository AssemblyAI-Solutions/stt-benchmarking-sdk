from setuptools import setup, find_packages

setup(
    name="stt-benchmarking-sdk",
    version="0.1.0",
    description="SDK for Speech-to-Text benchmarking with WER, CP-WER, and DER metrics",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jiwer>=3.0.0",
        "whisper-normalizer>=0.1.0",
        "thefuzz>=0.20.0",
        "python-Levenshtein>=0.20.0",
        "numpy>=1.20.0",
        "meeteval>=0.3.0",  # For CP-WER calculation
        "pyannote.metrics>=3.2.0",  # For DER calculation
        "pyannote.core>=5.0.0",  # Required by pyannote.metrics
        "scipy>=1.7.0",  # For optimal speaker mapping in DER
        "requests>=2.28.0",  # For LLM API calls
        "python-dotenv>=0.19.0",  # For environment configuration
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
