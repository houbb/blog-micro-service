# -*- coding: utf-8 -*-
import os
import re
import codecs

def extract_title_from_file(file_path):
    """Extract title from markdown file"""
    try:
        # Use codecs.open for Python 2 compatibility
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            # Read the first few lines, title is usually at the beginning
            content = f.read(500)
            # Use regex to match title
            match = re.search(r'title:\s*(.+)', content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print("Error reading {0}: {1}".format(file_path, e))
    return None

def generate_index_for_directory(dir_path, index_file_path):
    """Generate index file for directory"""
    # Get all md files in directory
    md_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
    
    # Sort files by name
    md_files.sort()
    
    # Extract title for each file
    file_titles = []
    for md_file in md_files:
        file_path = os.path.join(dir_path, md_file)
        title = extract_title_from_file(file_path)
        if title:
            file_titles.append((md_file, title))
    
    # Write index file
    with codecs.open(index_file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("title: API 网关文章索引\n")
        f.write("icon: list\n")
        f.write("---\n\n")
        f.write("# API 网关文章索引\n\n")
        f.write("API 网关是微服务架构中的关键组件，作为系统的统一入口点，负责请求路由、协议转换、负载均衡、安全控制、流量控制等功能。\n\n")
        f.write("## 文章列表\n\n")
        
        for md_file, title in file_titles:
            f.write("- [{0}]({1})\n".format(title, md_file))
        
        f.write("\n---\n\n")
        f.write("[返回上级目录](../)\n")

# Generate index for API Gateway directory
api_gateway_dir = r"d:\github\blog-micro-service\src\posts\api-gateway"
index_file = r"d:\github\blog-micro-service\src\posts\api-gateway\index.md"
generate_index_for_directory(api_gateway_dir, index_file)

print("API 网关索引文件生成完成")