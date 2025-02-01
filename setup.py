import setuptools
from pathlib import Path

# 获取当前目录路径
here = Path(__file__).parent.resolve()

# 读取 README 文件作为长描述
try:
    with open(here / "README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

# 读取 requirements.txt 中的依赖项
with open(here / "requirements.txt", encoding="utf-8") as f:
    install_requires = [
        line.strip() for line in f
        if line.strip() and not line.startswith("#")
    ]

setuptools.setup(
    name="citation_fetcher",  # 项目名称
    version="0.1.0",           # 版本号
    author="luxward",          # 作者姓名
    author_email="your.email@example.com",  # 作者邮箱
    description="A tool to fetch and manage citations.",  # 简短描述
    long_description=long_description,  # 长描述，从 README.md 读取
    long_description_content_type="text/markdown",
    url="https://github.com/luxward/citation-fetcher",  # 项目主页
    packages=setuptools.find_packages(),  # 自动发现项目包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 根据实际情况修改许可证
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 指定支持的 Python 版本
    install_requires=install_requires,  # 依赖项
    entry_points={
        'console_scripts': [
            'citation_fetcher=citation_fetcher.cli:main',  # 命令行入口（如果有）
        ],
    },
    include_package_data=True,  # 包含包内数据
    package_data={
        # 如果有需要包含的非 Python 文件，可以在这里指定
        # 例如：
        # '': ['*.txt', '*.md'],
    },
    license="MIT",  # 根据实际情况修改
    keywords="citation, fetch, tool",  # 相关关键词
    project_urls={  # 其他相关链接
        "Bug Reports": "https://github.com/luxward/citation-fetcher/issues",
        "Source": "https://github.com/luxward/citation-fetcher/",
    },
)