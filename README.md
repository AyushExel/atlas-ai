<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlas - Beautiful README</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #e2e8f0;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 60px;
        }
        
        .logo {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
            border-radius: 24px;
            margin: 0 auto 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: 700;
            color: white;
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
        }
        
        .badges {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 32px;
            flex-wrap: wrap;
        }
        
        .badge {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .badge:hover {
            background: rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }
        
        .hero-text {
            font-size: 20px;
            color: #cbd5e1;
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        
        /* Section Headers */
        .section {
            margin-bottom: 60px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 24px;
            position: relative;
            display: inline-block;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            border-radius: 2px;
        }
        
        /* Core Operations */
        .operations-grid {
            display: grid;
            gap: 32px;
            margin-bottom: 48px;
        }
        
        .operation-card {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 32px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .operation-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        }
        
        .operation-card:hover {
            transform: translateY(-4px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .operation-title {
            font-size: 24px;
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .operation-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .operation-desc {
            color: #cbd5e1;
            margin-bottom: 24px;
            font-size: 16px;
        }
        
        .flow-diagram {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 12px;
            padding: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #94a3b8;
            overflow-x: auto;
            border-left: 4px solid #6366f1;
        }
        
        /* Code Blocks */
        .code-section {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 16px;
            padding: 32px;
            margin: 32px 0;
            border: 1px solid rgba(99, 102, 241, 0.2);
            position: relative;
        }
        
        .code-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #10b981, #059669);
            border-radius: 16px 16px 0 0;
        }
        
        .code-block {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            padding: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #e2e8f0;
            overflow-x: auto;
            border-left: 4px solid #10b981;
            position: relative;
        }
        
        .code-block::before {
            content: 'Python';
            position: absolute;
            top: -12px;
            right: 16px;
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        /* Syntax Highlighting */
        .keyword { color: #c084fc; font-weight: 500; }
        .string { color: #34d399; }
        .comment { color: #64748b; font-style: italic; }
        .function { color: #60a5fa; }
        .variable { color: #f1f5f9; }
        
        /* Data Tables */
        .data-table {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #cbd5e1;
            overflow-x: auto;
            margin: 20px 0;
            border: 1px solid rgba(252, 211, 77, 0.3);
        }
        
        /* Installation Section */
        .install-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin: 32px 0;
        }
        
        .install-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
        }
        
        .install-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
        }
        
        .install-title {
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .bash-code {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 8px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #10b981;
            border-left: 4px solid #10b981;
        }
        
        /* Collapsible Sections */
        .collapsible {
            background: rgba(30, 41, 59, 0.3);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            margin: 16px 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .collapsible:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .collapsible-header {
            padding: 20px 24px;
            background: rgba(99, 102, 241, 0.1);
            cursor: pointer;
            font-weight: 600;
            color: #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        
        .collapsible-header:hover {
            background: rgba(99, 102, 241, 0.15);
        }
        
        .collapsible-content {
            padding: 24px;
            border-top: 1px solid rgba(99, 102, 241, 0.1);
        }
        
        /* Visual Enhancements */
        .highlight-box {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
        }
        
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 32px 0;
        }
        
        .feature-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            background: rgba(30, 41, 59, 0.3);
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }
        
        .feature-icon {
            color: #10b981;
            font-size: 20px;
            margin-top: 2px;
        }
        
        .feature-text {
            color: #cbd5e1;
        }
        
        .feature-title {
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 4px;
        }
        
        /* Coming Soon Sections */
        .coming-soon {
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
            border: 2px dashed rgba(251, 191, 36, 0.3);
            border-radius: 16px;
            padding: 48px;
            text-align: center;
            margin: 40px 0;
        }
        
        .coming-soon-title {
            font-size: 24px;
            font-weight: 600;
            color: #fbbf24;
            margin-bottom: 12px;
        }
        
        .coming-soon-text {
            color: #cbd5e1;
            font-size: 16px;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 20px 16px;
            }
            
            .badges {
                flex-direction: column;
                align-items: center;
            }
            
            .install-grid {
                grid-template-columns: 1fr;
            }
            
            .section-title {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">A</div>
            
            <div class="badges">
                <a href="https://pypi.org/project/atlas-ai/" class="badge">📦 PyPI Version</a>
                <a href="https://github.com/your-repo/atlas/actions" class="badge">🔄 CI Status</a>
                <a href="https://codecov.io/gh/your-repo/atlas" class="badge">📊 Code Coverage</a>
            </div>
            
            <div class="hero-text">
                Atlas is a data-centric AI framework for curating, indexing, and analyzing massive datasets for deep learning applications. It provides a suite of tools to streamline the entire data lifecycle, from initial data ingestion to model training and analysis.
            </div>
        </div>

        <!-- Core Operations -->
        <div class="section">
            <h2 class="section-title">Core Operations</h2>
            <p style="color: #cbd5e1; margin-bottom: 32px; font-size: 18px;">
                The vision for Atlas is to provide a comprehensive solution for managing large-scale datasets in AI development. The framework is built around three core operations:
            </p>
            
            <div class="operations-grid">
                <div class="operation-card">
                    <div class="operation-title">
                        <div class="operation-icon">📥</div>
                        Sink
                    </div>
                    <div class="operation-desc">
                        Ingest data from any source and format into an optimized Lance dataset.
                    </div>
                    <div class="flow-diagram">
+-----------------------+      +----------------------+      +---------------------+
|   Raw Data Sources    |      |      Atlas Sink      |      |   Lance Dataset     |
|  (COCO, YOLO, CSV)    |----->|  (Auto-detection,    |----->|  (Optimized Storage)|
|                       |      |   Metadata Extraction)|      |                     |
+-----------------------+      +----------------------+      +---------------------+
                    </div>
                </div>

                <div class="operation-card">
                    <div class="operation-title">
                        <div class="operation-icon">🔍</div>
                        Index
                    </div>
                    <div class="operation-desc">
                        Create powerful, multi-modal indexes (FTS/BM25, Vector embeddings, Hybrid, or custom features) on your data to enable fast and efficient search and retrieval.
                    </div>
                    <div class="flow-diagram">
+---------------------+      +----------------------+      +-----------------------------+
|   Lance Dataset     |      |       Index          |      |   Indexed Dataset           |
| (Optimized Storage) |----->|  (Vector & Metadata  |----->| (Vector Search, SQL Filters)|
| (Larger than memory)|      |      Indexing)       |      | (For massive datasets)      |
+---------------------+      +----------------------+      +-----------------------------+
                    </div>
                </div>

                <div class="operation-card">
                    <div class="operation-title">
                        <div class="operation-icon">📊</div>
                        Analyse
                    </div>
                    <div class="operation-desc">
                        Analyse your datasets to gain insights, identify patterns, and debug your models (Run EDA and filters of larger-than-memory datasets).
                    </div>
                    <div class="flow-diagram">
+-----------------------+      +------------------------+      +----------------------+
|   Indexed Dataset     |      |     Atlas Analyse      |      |   Insights &         |
|    (Fast Queries)     |----->| (Embedding Analysis,   |----->|   Visualizations     |
|                       |      |  Quality Checks, etc.) |      |                      |
+-----------------------+      +------------------------+      +----------------------+
                    </div>
                </div>

                <div class="operation-card">
                    <div class="operation-title">
                        <div class="operation-icon">🚀</div>
                        Training
                    </div>
                    <div class="operation-desc">
                        Connect with your desired trainer and directly train from your sink source without any transformation required.
                    </div>
                    <div class="flow-diagram">
+-----------------------+      +------------------------+      +----------------------+
|   Indexed Dataset     |      |      Trainer           |      |   Insights &         |
|    (Fast Queries)     |----->| (PyTorch, TF, etc.)    |----->|   Models             |
|                       |      |                        |      |                      |
+-----------------------+      +------------------------+      +----------------------+
                    </div>
                </div>
            </div>

            <div class="highlight-box">
                <h3 style="color: #f1f5f9; margin-bottom: 16px;">📋 End-to-End Example</h3>
                <p style="color: #cbd5e1; margin-bottom: 20px;">Here is an end-to-end example of how to <strong>sink</strong> a dataset and then <strong>index</strong> it:</p>
                
                <div class="code-block">
<span class="keyword">import</span> <span class="string">atlas</span>
<span class="keyword">from</span> <span class="string">atlas.index</span> <span class="keyword">import</span> <span class="function">Indexer</span>
<span class="keyword">from</span> <span class="string">datasets</span> <span class="keyword">import</span> <span class="function">load_dataset</span>

<span class="comment"># --- 1. Sink a dataset from Hugging Face Hub ---</span>
<span class="comment"># We'll use a dataset with images and text captions.</span>
<span class="variable">dataset</span> = <span class="function">load_dataset</span>(<span class="string">"lambdalabs/pokemon-blip-captions"</span>, split=<span class="string">"train"</span>)
<span class="function">atlas.sink</span>(<span class="variable">dataset</span>, <span class="string">"pokemon.lance"</span>)

<span class="comment"># --- 2. Initialize the Indexer ---</span>
<span class="variable">idx</span> = <span class="function">Indexer</span>(<span class="string">"pokemon.lance"</span>)

<span class="comment"># --- 3. Create Indexes ---</span>
<span class="variable">idx</span>.<span class="function">create_index</span>(column=<span class="string">"image"</span>, index_type=<span class="string">"vector"</span>)
<span class="variable">idx</span>.<span class="function">create_index</span>(column=<span class="string">"text"</span>, index_type=<span class="string">"fts"</span>)

<span class="comment"># --- 4. List and verify indexes ---</span>
<span class="variable">idx</span>.<span class="function">list_indexes</span>()
                </div>

                <div class="data-table">
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Column Name ┃ Data Type                         ┃ Index Type ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⇇━━━━━━━━━━━━┩
│ image       │ binary                            │ None       │
│ text        │ string                            │ text_idx   │
│ vector      │ fixed_size_list<item: float>[768] │ vector_idx │
└─────────────┴───────────────────────────────────┴────────────┘
                </div>
            </div>
        </div>

        <!-- Sink Section -->
        <div class="section">
            <h2 class="section-title">Sink</h2>
            <p style="color: #cbd5e1; margin-bottom: 32px; font-size: 18px;">
                The <strong>Sink</strong> operation allows you to ingest data from any source and format into an optimized Lance dataset. Atlas automatically infers the dataset type, extracts rich metadata, and stores the data in a self-contained, portable format.
            </p>

            <div class="feature-list">
                <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <div>
                        <div class="feature-title">Automatic Data Ingestion</div>
                        <div class="feature-text">The sink command automatically detects the dataset type (e.g., COCO, YOLO, CSV) and infers the optimal way to ingest the data into Lance.</div>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🏷️</div>
                    <div>
                        <div class="feature-title">Rich Metadata Extraction</div>
                        <div class="feature-text">Atlas extracts a wide range of metadata from your datasets, including image dimensions, class names, captions, and keypoints.</div>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📦</div>
                    <div>
                        <div class="feature-title">Self-Contained Datasets</div>
                        <div class="feature-text">All data, including images and other binary assets, is stored directly in the Lance dataset, making it easy to share and version your data.</div>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🔧</div>
                    <div>
                        <div class="feature-title">Extensible Architecture</div>
                        <div class="feature-text">The framework is designed to be easily extensible, allowing you to add support for new data formats, tasks, and indexing strategies.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Installation -->
        <div class="section">
            <h2 class="section-title">Installation</h2>
            <p style="color: #cbd5e1; margin-bottom: 24px;">To use Atlas, you need to have FFmpeg installed on your system.</p>
            
            <div class="install-grid">
                <div class="install-card">
                    <div class="install-title">🍎 macOS</div>
                    <div class="bash-code">brew install ffmpeg</div>
                </div>
                <div class="install-card">
                    <div class="install-title">🐧 Linux</div>
                    <div class="bash-code">sudo apt-get install ffmpeg</div>
                </div>
            </div>

            <div class="highlight-box">
                <p style="color: #cbd5e1; margin-bottom: 16px;">If you have installed ffmpeg and are still seeing errors, you may need to set the <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #fbbf24;">DYLD_LIBRARY_PATH</code> environment variable:</p>
                <div class="bash-code">export DYLD_LIBRARY_PATH=$(brew --prefix)/lib:$DYLD_LIBRARY_PATH</div>
            </div>

            <div class="install-grid">
                <div class="install-card">
                    <div class="install-title">📦 Install Atlas</div>
                    <div class="bash-code">pip install atlas-ai</div>
                </div>
                <div class="install-card">
                    <div class="install-title">🎵 With Audio Support</div>
                    <div class="bash-code">pip install atlas-ai[audio]</div>
                </div>
            </div>
        </div>

        <!-- Usage Section -->
        <div class="section">
            <h2 class="section-title">Usage</h2>
            
            <div class="code-section">
                <h3 style="color: #f1f5f9; margin-bottom: 16px;">🐍 Python API (Recommended)</h3>
                <p style="color: #cbd5e1; margin-bottom: 20px;">The atlas Python API provides a flexible and powerful way to sink your datasets.</p>
                
                <div class="highlight-box">
                    <h4 style="color: #f1f5f9; margin-bottom: 12px;">🤗 Sinking from Hugging Face Datasets</h4>
                    <p style="color: #cbd5e1; margin-bottom: 16px;">This is the recommended way to use Atlas. You can sink a dataset directly from the Hugging Face Hub.</p>
                    
                    <div class="code-block">
<span class="keyword">from</span> <span class="string">datasets</span> <span class="keyword">import</span> <span class="function">load_dataset</span>
<span class="keyword">import</span> <span class="string">atlas</span>

<span class="comment"># Load dataset from Hugging Face</span>
<span class="variable">dataset</span> = <span class="function">load_dataset</span>(<span class="string">"lambdalabs/pokemon-blip-captions"</span>, split=<span class="string">"train"</span>)

<span class="comment"># Sink the dataset to Lance format</span>
<span class="function">atlas.sink</span>(<span class="variable">dataset</span>, <span class="string">"pokemon.lance"</span>)
                    </div>
                </div>

                <div class="data-table">
<strong>Sample Data:</strong>
+------------------------------------+------------------+---------+----------+------------------------------------------------------------+
| image                              | file_name        |   width |   height | label                                                      |
+====================================+==================+=========+==========+============================================================+
| b'\xff\xd8\xff\xe0\x00\x10JFIF'... | 000000397133.jpg |     640 |      427 | [44 67  1 49 51 51 79  1 47 47 51 51 56 50 56 56 79 57 81] |
+------------------------------------+------------------+---------+----------+------------------------------------------------------------+
                </div>
            </div>

            <!-- Collapsible sections -->
            <div class="collapsible">
                <div class="collapsible-header">
                    🔄 Automatically expand nested schemas
                </div>
                <div class="collapsible-content">
                    <p style="color: #cbd5e1; margin-bottom: 16px;">For nested Hugging Face datasets, you can use the <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #fbbf24;">expand_level</code> argument to flatten the structure.</p>
                    
                    <div class="code-block">
<span class="keyword">from</span> <span class="string">datasets</span> <span class="keyword">import</span> <span class="function">Dataset</span>, <span class="function">Features</span>, <span class="function">Value</span>
<span class="keyword">import</span> <span class="string">atlas</span>

<span class="variable">data</span> = [
    {<span class="string">"nested"</span>: {<span class="string">"a"</span>: 1, <span class="string">"b"</span>: <span class="string">"one"</span>}},
    {<span class="string">"nested"</span>: {<span class="string">"a"</span>: 2, <span class="string">"b"</span>: <span class="string">"two"</span>, <span class="string">"c"</span>: <span class="keyword">True</span>}},
    {<span class="string">"nested"</span>: {<span class="string">"a"</span>: 3}},
    {},
]

<span class="comment"># Sink with expansion</span>
<span class="function">atlas.sink</span>(<span class="variable">dataset</span>, <span class="string">"expanded.lance"</span>, task=<span class="string">"hf"</span>, expand_level=1, handle_nested_nulls=<span class="keyword">True</span>)
                    </div>
                </div>
            </div>

            <div class="collapsible">
                <div class="collapsible-header">
                    📁 Task-based or File-format based sinks
                </div>
                <div class="collapsible-content">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div class="install-card">
                            <div class="install-title">🎯 Object Detection (COCO)</div>
                            <div class="code-block" style="font-size: 12px;">atlas.sink("examples/data/coco/annotations/instances_val2017_small.json")</div>