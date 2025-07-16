// Multi-platform Social Media Post Generator - Frontend JavaScript

class PostGenerator {
    constructor() {
        this.currentTab = 'note';
        this.generatedContent = {};
        this.sampleArticles = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupCharCounters();
        this.setupFileUpload();
        this.loadDefaultContent();
        this.setupMobileOptimizations();
        this.registerServiceWorker();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const platform = e.currentTarget.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.switchTab(platform);
            });
        });

        // Generate button
        document.querySelector('.generate-btn').addEventListener('click', () => {
            this.generateContent();
        });

        // Modal close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.generateContent();
            }
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    setupCharCounters() {
        const textareas = ['theme', 'style-guide', 'sns-workflow'];
        textareas.forEach(id => {
            const textarea = document.getElementById(id);
            const counter = document.getElementById(id + '-count');
            
            if (textarea && counter) {
                textarea.addEventListener('input', () => {
                    const count = textarea.value.length;
                    counter.textContent = `${count}文字`;
                    
                    // Visual feedback for length
                    if (count > 1000) {
                        counter.style.color = '#e74c3c';
                    } else if (count > 500) {
                        counter.style.color = '#f39c12';
                    } else {
                        counter.style.color = '#666';
                    }
                });
            }
        });
    }

    setupFileUpload() {
        const fileInput = document.getElementById('file-input');
        const uploadDropZone = document.querySelector('.upload-drop-zone');

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Drag and drop
        uploadDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadDropZone.style.borderColor = '#667eea';
            uploadDropZone.style.background = 'rgba(102, 126, 234, 0.1)';
        });

        uploadDropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadDropZone.style.borderColor = '#ccc';
            uploadDropZone.style.background = 'rgba(255, 255, 255, 0.5)';
        });

        uploadDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadDropZone.style.borderColor = '#ccc';
            uploadDropZone.style.background = 'rgba(255, 255, 255, 0.5)';
            this.handleFileUpload(e.dataTransfer.files);
        });
    }

    loadDefaultContent() {
        // Load default content from existing files
        const defaultTheme = `営業の自動化について書きたい

具体的には：
- 営業プロセスの自動化ツール
- 顧客管理システム（CRM）の活用
- AI技術を使った営業支援
- 実際に導入してみた結果や効果
- 自動化によって生まれる時間をどう活用するか`;

        const defaultStyleGuide = `## 基本情報
- 名前：はる
- 経営：合同会社アークスの代表
- 特徴：AIや自動化ツールが好きで、積極的に活用している

## 執筆スタイル
- フレンドリーで親しみやすいトーン
- 実際の経験に基づいた具体的なエピソードを交える
- 読者との対話を意識した表現（「〜ですよね？」「〜しませんか？」など）
- 絵文字を適度に使用（例：😊、💪）
- 専門用語は分かりやすく説明`;

        const defaultWorkflow = `## プラットフォーム別特徴

### note
- **目的**: 深い内容の共有、思考の整理
- **文字数**: 800-1500文字
- **構成**: 問題提起 → 体験談 → 解決策 → まとめ

### LinkedIn
- **目的**: ビジネス関連の知見共有
- **文字数**: 300-600文字
- **構成**: 結論先出し → 根拠 → 行動提案

### Twitter/X
- **目的**: 気づきの共有、エンゲージメント
- **文字数**: 140文字×1-3連投
- **構成**: インパクト重視 → 補足説明`;

        document.getElementById('theme').value = defaultTheme;
        document.getElementById('style-guide').value = defaultStyleGuide;
        document.getElementById('sns-workflow').value = defaultWorkflow;

        // Trigger char counters
        this.setupCharCounters();
        document.getElementById('theme').dispatchEvent(new Event('input'));
        document.getElementById('style-guide').dispatchEvent(new Event('input'));
        document.getElementById('sns-workflow').dispatchEvent(new Event('input'));
    }

    switchTab(platform) {
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[onclick="switchTab('${platform}')"]`).classList.add('active');

        // Update active panel
        document.querySelectorAll('.output-panel').forEach(panel => panel.classList.remove('active'));
        document.getElementById(`${platform}-output`).classList.add('active');

        this.currentTab = platform;
    }

    async generateContent() {
        const generateBtn = document.querySelector('.generate-btn');
        const statusIndicator = document.getElementById('status-indicator');

        try {
            // Validate inputs
            const theme = document.getElementById('theme').value.trim();
            const styleGuide = document.getElementById('style-guide').value.trim();
            const snsWorkflow = document.getElementById('sns-workflow').value.trim();

            if (!theme || !styleGuide || !snsWorkflow) {
                this.showError('すべての必須項目を入力してください');
                return;
            }

            // Show loading state
            this.showLoading(true);
            generateBtn.disabled = true;
            statusIndicator.className = 'status-indicator generating';
            statusIndicator.querySelector('.status-text').textContent = '生成中...';

            // Prepare request data
            const requestData = {
                theme: theme,
                style_guide: styleGuide,
                sns_workflow: snsWorkflow,
                sample_articles: this.sampleArticles,
                model_type: document.getElementById('model-type').value
            };

            // Send request
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result);
                statusIndicator.className = 'status-indicator success';
                statusIndicator.querySelector('.status-text').textContent = '生成完了';
            } else {
                throw new Error(result.error || '生成に失敗しました');
            }

        } catch (error) {
            console.error('Generation error:', error);
            this.showError(error.message);
            statusIndicator.className = 'status-indicator error';
            statusIndicator.querySelector('.status-text').textContent = 'エラー';
        } finally {
            this.showLoading(false);
            generateBtn.disabled = false;
        }
    }

    displayResults(result) {
        this.generatedContent = result.content;

        // Display content for each platform
        ['note', 'linkedin', 'twitter'].forEach(platform => {
            const contentElement = document.getElementById(`${platform}-text`);
            const statsElement = document.getElementById(`${platform}-stats`);
            const downloadBtn = contentElement.parentElement.querySelector('.download-btn');

            if (result.content[platform]) {
                const platformData = result.content[platform];
                
                // Remove placeholder and show content
                contentElement.innerHTML = platformData.content;
                contentElement.classList.add('fade-in');

                // Show stats
                const validation = platformData.validation;
                const statsHTML = `
                    <div class="stat-item">
                        <i class="fas fa-text-width"></i>
                        <span>${platformData.char_count}文字</span>
                    </div>
                    ${validation.warnings.length > 0 ? 
                        validation.warnings.map(warning => 
                            `<div class="stat-item stat-warning">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>${warning}</span>
                            </div>`
                        ).join('') : 
                        `<div class="stat-item stat-success">
                            <i class="fas fa-check-circle"></i>
                            <span>適切な長さです</span>
                        </div>`
                    }
                `;
                
                statsElement.innerHTML = statsHTML;
                downloadBtn.disabled = false;
            }
        });

        // Show model info
        if (result.model_used) {
            const modelInfo = document.createElement('div');
            modelInfo.className = 'model-info';
            modelInfo.innerHTML = `
                <small style="color: #666; font-size: 0.8rem;">
                    <i class="fas fa-robot"></i> 生成モデル: ${result.model_used} | 
                    生成時間: ${new Date(result.generated_at).toLocaleTimeString()}
                </small>
            `;
            
            // Add to current tab
            const currentPanel = document.getElementById(`${this.currentTab}-output`);
            const existing = currentPanel.querySelector('.model-info');
            if (existing) existing.remove();
            currentPanel.appendChild(modelInfo);
        }
    }

    async downloadContent(platform) {
        try {
            if (!this.generatedContent[platform]) {
                this.showError('ダウンロードするコンテンツがありません');
                return;
            }

            const content = this.generatedContent[platform].content;
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            
            const filenameMap = {
                'note': `note_draft_${timestamp}.md`,
                'linkedin': `linkedin_post_${timestamp}.txt`,
                'twitter': `twitter_thread_${timestamp}.txt`
            };

            // Create and download file
            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filenameMap[platform];
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess(`${platform}の投稿をダウンロードしました`);

        } catch (error) {
            console.error('Download error:', error);
            this.showError('ダウンロードに失敗しました');
        }
    }

    async handleFileUpload(files) {
        for (let file of files) {
            if (!file.name.match(/\.(txt|md)$/i)) {
                this.showError(`${file.name}: 対応していないファイル形式です`);
                continue;
            }

            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('file_type', 'sample_article');

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    this.addSampleArticle(result);
                    this.showSuccess(`${result.filename} をアップロードしました`);
                } else {
                    throw new Error(result.error);
                }

            } catch (error) {
                console.error('Upload error:', error);
                this.showError(`${file.name}: アップロードに失敗しました`);
            }
        }

        this.closeModal();
    }

    addSampleArticle(articleData) {
        this.sampleArticles.push({
            filename: articleData.filename,
            content: articleData.content,
            char_count: articleData.char_count
        });

        const listContainer = document.getElementById('sample-articles-list');
        const articleElement = document.createElement('div');
        articleElement.className = 'sample-article-item';
        articleElement.innerHTML = `
            <div class="article-info">
                <i class="fas fa-file-alt"></i>
                <span>${articleData.filename}</span>
                <small>(${articleData.char_count}文字)</small>
            </div>
            <i class="fas fa-times remove-article" onclick="postGenerator.removeSampleArticle('${articleData.filename}')"></i>
        `;

        listContainer.appendChild(articleElement);
    }

    removeSampleArticle(filename) {
        this.sampleArticles = this.sampleArticles.filter(article => article.filename !== filename);
        
        const listContainer = document.getElementById('sample-articles-list');
        const articleElements = listContainer.querySelectorAll('.sample-article-item');
        
        articleElements.forEach(element => {
            if (element.querySelector('.article-info span').textContent === filename) {
                element.remove();
            }
        });
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showModal() {
        document.getElementById('upload-modal').style.display = 'flex';
    }

    closeModal() {
        document.getElementById('upload-modal').style.display = 'none';
        document.getElementById('file-input').value = '';
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add styles if not exists
        if (!document.querySelector('.notification-styles')) {
            const styles = document.createElement('style');
            styles.className = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    z-index: 9999;
                    border-left: 4px solid #667eea;
                    animation: slideIn 0.3s ease;
                    max-width: calc(100vw - 40px);
                }
                @media (max-width: 768px) {
                    .notification {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }
                }
                .notification.success {
                    border-left-color: #27ae60;
                }
                .notification.error {
                    border-left-color: #e74c3c;
                }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 1rem 1.5rem;
                }
                .notification-close {
                    background: none;
                    border: none;
                    cursor: pointer;
                    color: #999;
                    margin-left: auto;
                    min-width: 44px;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    setupMobileOptimizations() {
        // Prevent zoom on iOS when focusing input
        const preventZoom = (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                e.target.style.fontSize = '16px';
            }
        };

        document.addEventListener('focusin', preventZoom);

        // Add touch feedback
        document.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('tab-btn') || 
                e.target.classList.contains('generate-btn') || 
                e.target.classList.contains('download-btn') ||
                e.target.classList.contains('upload-btn')) {
                e.target.style.transform = 'scale(0.98)';
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('tab-btn') || 
                e.target.classList.contains('generate-btn') || 
                e.target.classList.contains('download-btn') ||
                e.target.classList.contains('upload-btn')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            }
        });

        // Prevent double-tap zoom
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);

        // Add pull-to-refresh prevention
        let startY;
        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].pageY;
        });

        document.addEventListener('touchmove', (e) => {
            const y = e.touches[0].pageY;
            if (window.scrollY === 0 && y > startY) {
                e.preventDefault();
            }
        }, { passive: false });

        // Detect mobile orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Recalculate heights after orientation change
                this.adjustMobileLayout();
            }, 500);
        });
    }

    adjustMobileLayout() {
        // Adjust output text height on mobile
        const outputTexts = document.querySelectorAll('.output-text');
        outputTexts.forEach(text => {
            const isMobile = window.innerWidth <= 768;
            if (isMobile) {
                text.style.minHeight = '150px';
                text.style.maxHeight = '300px';
                text.style.overflowY = 'auto';
            }
        });
    }

    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then((registration) => {
                    console.log('SW registered successfully');
                })
                .catch((error) => {
                    console.log('SW registration failed');
                });
        }

        // Add install prompt for PWA
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            this.showInstallButton(deferredPrompt);
        });
    }

    showInstallButton(deferredPrompt) {
        const installBtn = document.createElement('button');
        installBtn.className = 'install-btn';
        installBtn.innerHTML = '<i class="fas fa-download"></i> アプリとしてインストール';
        installBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 25px;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
            font-size: 0.9rem;
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;

        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                if (outcome === 'accepted') {
                    installBtn.remove();
                }
                deferredPrompt = null;
            }
        });

        document.body.appendChild(installBtn);

        // Auto hide after 10 seconds
        setTimeout(() => {
            if (installBtn.parentElement) {
                installBtn.remove();
            }
        }, 10000);
    }
}

// Global functions for HTML onclick events
function switchTab(platform) {
    postGenerator.switchTab(platform);
}

function generateContent() {
    postGenerator.generateContent();
}

function downloadContent(platform) {
    postGenerator.downloadContent(platform);
}

function uploadFile(type) {
    postGenerator.showModal();
}

function closeModal() {
    postGenerator.closeModal();
}

// Initialize the application
let postGenerator;
document.addEventListener('DOMContentLoaded', () => {
    postGenerator = new PostGenerator();
});