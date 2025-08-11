// API基础URL
const API_BASE_URL = '';

// 全局变量
let uploadedResume = null;
let uploadedResumeName = null;

// DOM元素
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');
const progressOverlay = document.getElementById('progress-overlay');
const resultModal = document.getElementById('result-modal');
const resultContent = document.getElementById('result-content');
const closeModal = document.querySelector('.close');
const uploadBtn = document.getElementById('upload-btn');
const resumeUpload = document.getElementById('resume-upload');
const uploadStatus = document.getElementById('upload-status');
const generateButtons = {
    description: document.getElementById('description-generate-btn'),
    url: document.getElementById('url-generate-btn'),
    template: document.getElementById('template-generate-btn')
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化标签页
    initTabs();
    
    // 绑定上传事件
    bindUploadEvents();
    
    // 绑定表单提交事件
    bindFormEvents();
    
    // 加载模板列表
    loadTemplates();
    
    // 加载历史记录
    loadHistory();
    
    // 绑定刷新按钮事件
    bindRefreshEvents();
    
    // 绑定模态框关闭事件
    if (closeModal) {
        closeModal.addEventListener('click', () => {
            resultModal.classList.add('hidden');
        });
    }
    
    // 点击模态框外部关闭
    window.addEventListener('click', (event) => {
        if (event.target === resultModal) {
            resultModal.classList.add('hidden');
        }
    });
});

// 初始化标签页
function initTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // 更新活动标签按钮
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // 显示对应的标签内容
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === tabId + '-tab') {
                    pane.classList.add('active');
                }
            });
        });
    });
}

// 绑定上传事件
function bindUploadEvents() {
    if (uploadBtn) {
        uploadBtn.addEventListener('click', handleResumeUpload);
    }
}

// 绑定表单提交事件
function bindFormEvents() {
    // 职位描述表单
    const descriptionForm = document.getElementById('description-form');
    if (descriptionForm) {
        descriptionForm.addEventListener('submit', handleDescriptionSubmit);
    }
    
    // 职位链接表单
    const urlForm = document.getElementById('url-form');
    if (urlForm) {
        urlForm.addEventListener('submit', handleUrlSubmit);
    }
    
    // 模板表单
    const templateForm = document.getElementById('template-form');
    if (templateForm) {
        templateForm.addEventListener('submit', handleTemplateSubmit);
    }
}

// 绑定刷新按钮事件
function bindRefreshEvents() {
    const refreshTemplatesBtn = document.getElementById('refresh-templates');
    if (refreshTemplatesBtn) {
        refreshTemplatesBtn.addEventListener('click', loadTemplates);
    }
    
    const refreshHistoryBtn = document.getElementById('refresh-history');
    if (refreshHistoryBtn) {
        refreshHistoryBtn.addEventListener('click', loadHistory);
    }
}

// 处理简历上传
async function handleResumeUpload() {
    const file = resumeUpload.files[0];
    
    if (!file) {
        showMessage('请选择简历文件', 'error');
        return;
    }
    
    // 简单的文件类型检查
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('请上传PDF或DOCX格式的文件', 'error');
        return;
    }
    
    // 显示上传状态
    uploadStatus.textContent = '正在上传...';
    uploadStatus.className = '';
    
    try {
        // 在实际应用中，这里应该上传文件到服务器
        // 为简化起见，我们只是在前端保存文件引用
        uploadedResume = file;
        uploadedResumeName = file.name;
        
        // 更新生成按钮状态
        Object.values(generateButtons).forEach(btn => {
            if (btn) btn.disabled = false;
        });
        
        uploadStatus.textContent = `简历上传成功: ${file.name}`;
        uploadStatus.className = 'upload-success';
        
        showMessage('简历上传成功', 'success');
    } catch (error) {
        uploadStatus.textContent = '上传失败: ' + error.message;
        uploadStatus.className = 'upload-error';
        showMessage('简历上传失败: ' + error.message, 'error');
    }
}

// 处理职位描述表单提交
async function handleDescriptionSubmit(event) {
    event.preventDefault();
    
    if (!uploadedResume) {
        showMessage('请先上传简历', 'error');
        return;
    }
    
    const description = document.getElementById('job-description').value;
    
    if (!description) {
        showMessage('请填写职位描述', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('description', description);
    formData.append('resume', uploadedResume, uploadedResumeName);
    
    await generateResume('/generate-by-description', formData, '职位描述');
}

// 处理职位链接表单提交
async function handleUrlSubmit(event) {
    event.preventDefault();
    
    if (!uploadedResume) {
        showMessage('请先上传简历', 'error');
        return;
    }
    
    const url = document.getElementById('job-url').value;
    
    if (!url) {
        showMessage('请填写职位链接', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('url', url);
    formData.append('resume', uploadedResume, uploadedResumeName);
    
    await generateResume('/generate-by-url', formData, '职位链接');
}

// 处理模板表单提交
async function handleTemplateSubmit(event) {
    event.preventDefault();
    
    if (!uploadedResume) {
        showMessage('请先上传简历', 'error');
        return;
    }
    
    const templateName = document.getElementById('template-select').value;
    
    if (!templateName) {
        showMessage('请选择模板', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('template_name', templateName);
    formData.append('resume', uploadedResume, uploadedResumeName);
    
    await generateResume('/generate-by-template', formData, '模板');
}

// 生成简历的通用函数
async function generateResume(endpoint, formData, type) {
    try {
        // 显示进度指示器
        showProgress();
        
        // 发送请求
        const response = await fetch(API_BASE_URL + endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // 隐藏进度指示器
        hideProgress();
        
        if (result.success) {
            // 显示结果
            showResult(result, type);
            // 重新加载历史记录
            loadHistory();
        } else {
            showMessage(result.message || '生成失败', 'error');
        }
    } catch (error) {
        hideProgress();
        showMessage(`请求失败: ${error.message}`, 'error');
        console.error('Error:', error);
    }
}

// 显示进度指示器
function showProgress() {
    progressOverlay.classList.remove('hidden');
}

// 隐藏进度指示器
function hideProgress() {
    progressOverlay.classList.add('hidden');
}

// 显示结果
function showResult(result, type) {
    let content = `
        <div class="result-section">
            <h3>生成成功</h3>
            <p>通过${type}方式生成简历成功！</p>
        </div>
        
        <div class="result-section">
            <h3>匹配度评分</h3>
            <div class="match-score">${result.match_score}%</div>
        </div>
    `;
    
    if (result.suggestions && result.suggestions.length > 0) {
        content += `
            <div class="result-section">
                <h3>优化建议</h3>
                <ul class="suggestion-list">
                    ${result.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.ats_suggestions && result.ats_suggestions.length > 0) {
        content += `
            <div class="result-section">
                <h3>ATS优化建议</h3>
                <ul class="suggestion-list">
                    ${result.ats_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.generated_file) {
        content += `
            <div class="result-section">
                <h3>下载简历</h3>
                <p>
                    <a href="${API_BASE_URL}/download/${encodeURIComponent(result.generated_file)}" 
                       class="download-link" 
                       target="_blank">点击下载生成的简历</a>
                </p>
            </div>
        `;
    }
    
    resultContent.innerHTML = content;
    resultModal.classList.remove('hidden');
}

// 加载模板列表
async function loadTemplates() {
    try:
        const response = await fetch(API_BASE_URL + '/templates');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const templateSelect = document.getElementById('template-select');
        
        if (templateSelect && data.templates) {
            // 清空现有选项
            templateSelect.innerHTML = '<option value="">请选择模板</option>';
            
            // 添加模板选项
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template;
                option.textContent = template;
                templateSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载模板失败:', error);
        showMessage('加载模板列表失败', 'error');
    }
}

// 加载历史记录
async function loadHistory() {
    try {
        const response = await fetch(API_BASE_URL + '/history');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const historyList = document.getElementById('history-list');
        
        if (historyList && data.history) {
            if (data.history.length === 0) {
                historyList.innerHTML = '<p>暂无生成历史</p>';
                return;
            }
            
            // 按时间倒序排列
            const sortedHistory = data.history.sort((a, b) => 
                new Date(b.timestamp || 0) - new Date(a.timestamp || 0)
            );
            
            let historyHTML = '';
            sortedHistory.forEach(item => {
                historyHTML += `
                    <div class="history-item">
                        <h3>${getItemTitle(item)}</h3>
                        <p>生成方式: ${getItemType(item.type)}</p>
                        ${item.match_score ? `<p>匹配度: <span class="score">${item.match_score}%</span></p>` : ''}
                        <div class="meta">
                            <span>${formatDate(item.timestamp || new Date())}</span>
                            ${item.output ? `
                                <a href="${API_BASE_URL}/download/${encodeURIComponent(item.output)}" 
                                   class="download-link" 
                                   target="_blank">下载简历</a>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            historyList.innerHTML = historyHTML;
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
        const historyList = document.getElementById('history-list');
        if (historyList) {
            historyList.innerHTML = '<p class="error-message">加载历史记录失败</p>';
        }
    }
}

// 获取历史记录项标题
function getItemTitle(item) {
    switch (item.type) {
        case 'description':
            return '职位描述生成';
        case 'url':
            return '职位链接生成';
        case 'template':
            return `模板生成 (${item.input})`;
        default:
            return '未知类型';
    }
}

// 获取历史记录项类型描述
function getItemType(type) {
    switch (type) {
        case 'description':
            return '职位描述';
        case 'url':
            return '职位链接';
        case 'template':
            return '模板';
        default:
            return '未知';
    }
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 显示消息
function showMessage(message, type) {
    // 创建消息元素
    const messageElement = document.createElement('div');
    messageElement.className = type === 'error' ? 'error-message' : 'success-message';
    messageElement.textContent = message;
    
    // 插入到页面顶部
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(messageElement, container.firstChild);
        
        // 3秒后自动移除消息
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 3000);
    }
}