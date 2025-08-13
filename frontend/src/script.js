// API基础URL
const API_BASE_URL = '';

// 全局变量
let currentStep = 1;
let totalSteps = 4;
let resumeData = {};
let skills = [];
let uploadedResumeFile = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 绑定功能卡片点击事件
    bindActionCards();
    
    // 绑定技能输入事件
    bindSkillsInput();
    
    // 绑定文件上传事件
    bindFileUpload();
    
    // 绑定标签页切换
    bindTabSwitching();
    
    // 初始化拖拽上传
    initDragAndDrop();
    
    // 加载模板列表
    loadTemplates();
}

// 绑定功能卡片点击事件
function bindActionCards() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        card.addEventListener('click', () => {
            const action = card.getAttribute('data-action');
            handleActionCardClick(action);
        });
    });
}

// 处理功能卡片点击
function handleActionCardClick(action) {
    hideAllSections();
    
    switch(action) {
        case 'create-new':
            showSection('resume-builder');
            resetResumeBuilder();
            break;
        case 'upload-optimize':
            showSection('resume-optimizer');
            break;
        case 'job-match':
            showSection('job-matcher');
            break;
    }
}

// 隐藏所有区域
function hideAllSections() {
    const sections = ['welcome-section', 'resume-builder', 'resume-optimizer', 'job-matcher', 'result-section'];
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'none';
        }
    });
}

// 显示指定区域
function showSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = 'block';
        section.classList.add('fade-in');
    }
}

// 显示欢迎页面
function showWelcome() {
    hideAllSections();
    showSection('welcome-section');
}

// 重置简历制作器
function resetResumeBuilder() {
    currentStep = 1;
    updateProgressBar();
    showStep(1);
    clearFormData();
}

// 更新进度条
function updateProgressBar() {
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        const progress = (currentStep / totalSteps) * 100;
        progressFill.style.width = `${progress}%`;
    }
}

// 显示指定步骤
function showStep(step) {
    // 隐藏所有步骤
    const stepContents = document.querySelectorAll('.step-content');
    stepContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // 显示当前步骤
    const currentStepContent = document.getElementById(`step-${step}`);
    if (currentStepContent) {
        currentStepContent.classList.add('active');
    }
}

// 下一步
function nextStep() {
    if (validateCurrentStep()) {
        saveCurrentStepData();
        
        if (currentStep < totalSteps) {
            currentStep++;
            updateProgressBar();
            showStep(currentStep);
        }
    }
}

// 上一步
function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateProgressBar();
        showStep(currentStep);
    }
}

// 验证当前步骤
function validateCurrentStep() {
    switch(currentStep) {
        case 1:
            return validateBasicInfo();
        case 2:
            return true; // 工作经验可选
        case 3:
            return true; // 教育背景可选
        case 4:
            return true; // 技能可选
        default:
            return true;
    }
}

// 验证基本信息
function validateBasicInfo() {
    const requiredFields = ['name', 'email', 'phone', 'target-position'];
    let isValid = true;
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.value.trim()) {
            field.style.borderColor = '#ef4444';
            isValid = false;
        } else if (field) {
            field.style.borderColor = '#e5e7eb';
        }
    });
    
    if (!isValid) {
        showMessage('请填写所有必填项', 'error');
    }
    
    return isValid;
}

// 保存当前步骤数据
function saveCurrentStepData() {
    switch(currentStep) {
        case 1:
            saveBasicInfo();
            break;
        case 2:
            saveExperience();
            break;
        case 3:
            saveEducation();
            break;
        case 4:
            saveSkills();
            break;
    }
}

// 保存基本信息
function saveBasicInfo() {
    resumeData.basicInfo = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        targetPosition: document.getElementById('target-position').value,
        summary: document.getElementById('summary').value
    };
}

// 保存工作经验
function saveExperience() {
    const experienceItems = document.querySelectorAll('.experience-item');
    resumeData.experience = [];
    
    experienceItems.forEach(item => {
        const inputs = item.querySelectorAll('input, textarea');
        const experience = {};
        
        inputs.forEach(input => {
            if (input.value.trim()) {
                const key = input.placeholder || input.type;
                experience[key] = input.value;
            }
        });
        
        if (Object.keys(experience).length > 0) {
            resumeData.experience.push(experience);
        }
    });
}

// 保存教育背景
function saveEducation() {
    const educationItems = document.querySelectorAll('.education-item');
    resumeData.education = [];
    
    educationItems.forEach(item => {
        const inputs = item.querySelectorAll('input, select');
        const education = {};
        
        inputs.forEach(input => {
            if (input.value.trim()) {
                const key = input.placeholder || input.type;
                education[key] = input.value;
            }
        });
        
        if (Object.keys(education).length > 0) {
            resumeData.education.push(education);
        }
    });
}

// 保存技能
function saveSkills() {
    resumeData.skills = skills;
    
    const languageItems = document.querySelectorAll('.language-item');
    resumeData.languages = [];
    
    languageItems.forEach(item => {
        const selects = item.querySelectorAll('select');
        if (selects.length >= 2) {
            resumeData.languages.push({
                language: selects[0].value,
                level: selects[1].value
            });
        }
    });
}

// 绑定技能输入事件
function bindSkillsInput() {
    const skillInput = document.getElementById('skill-input');
    if (skillInput) {
        skillInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSkill();
            }
        });
    }
}

// 添加技能
function addSkill() {
    const skillInput = document.getElementById('skill-input');
    const skillsContainer = document.getElementById('skills-tags');
    
    if (skillInput && skillsContainer) {
        const skillText = skillInput.value.trim();
        
        if (skillText && !skills.includes(skillText)) {
            skills.push(skillText);
            
            const skillTag = document.createElement('div');
            skillTag.className = 'skill-tag';
            skillTag.innerHTML = `
                ${skillText}
                <button class="remove-btn" onclick="removeSkill('${skillText}')">&times;</button>
            `;
            
            skillsContainer.appendChild(skillTag);
            skillInput.value = '';
        }
    }
}

// 移除技能
function removeSkill(skillText) {
    const index = skills.indexOf(skillText);
    if (index > -1) {
        skills.splice(index, 1);
        
        // 重新渲染技能标签
        const skillsContainer = document.getElementById('skills-tags');
        if (skillsContainer) {
            skillsContainer.innerHTML = '';
            skills.forEach(skill => {
                const skillTag = document.createElement('div');
                skillTag.className = 'skill-tag';
                skillTag.innerHTML = `
                    ${skill}
                    <button class="remove-btn" onclick="removeSkill('${skill}')">&times;</button>
                `;
                skillsContainer.appendChild(skillTag);
            });
        }
    }
}

// 添加工作经验
function addExperience() {
    const experienceList = document.getElementById('experience-list');
    if (experienceList) {
        const experienceItem = document.createElement('div');
        experienceItem.className = 'experience-item';
        experienceItem.innerHTML = `
            <div class="form-grid">
                <div class="form-group">
                    <label>公司名称</label>
                    <input type="text" placeholder="公司名称">
                </div>
                <div class="form-group">
                    <label>职位</label>
                    <input type="text" placeholder="职位名称">
                </div>
                <div class="form-group">
                    <label>开始时间</label>
                    <input type="month">
                </div>
                <div class="form-group">
                    <label>结束时间</label>
                    <input type="month">
                </div>
            </div>
            <div class="form-group">
                <label>工作描述</label>
                <textarea placeholder="描述您的主要工作内容和成就"></textarea>
            </div>
            <button class="remove-btn" onclick="removeExperience(this)">删除</button>
        `;
        experienceList.appendChild(experienceItem);
    }
}

// 移除工作经验
function removeExperience(button) {
    const experienceItem = button.closest('.experience-item');
    if (experienceItem) {
        experienceItem.remove();
    }
}

// 添加教育经历
function addEducation() {
    const educationList = document.getElementById('education-list');
    if (educationList) {
        const educationItem = document.createElement('div');
        educationItem.className = 'education-item';
        educationItem.innerHTML = `
            <div class="form-grid">
                <div class="form-group">
                    <label>学校名称</label>
                    <input type="text" placeholder="学校名称">
                </div>
                <div class="form-group">
                    <label>专业</label>
                    <input type="text" placeholder="专业名称">
                </div>
                <div class="form-group">
                    <label>学历</label>
                    <select>
                        <option>本科</option>
                        <option>硕士</option>
                        <option>博士</option>
                        <option>专科</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>毕业时间</label>
                    <input type="month">
                </div>
            </div>
            <button class="remove-btn" onclick="removeEducation(this)">删除</button>
        `;
        educationList.appendChild(educationItem);
    }
}

// 移除教育经历
function removeEducation(button) {
    const educationItem = button.closest('.education-item');
    if (educationItem) {
        educationItem.remove();
    }
}

// 添加语言
function addLanguage() {
    const languageList = document.getElementById('language-list');
    if (languageList) {
        const languageItem = document.createElement('div');
        languageItem.className = 'language-item';
        languageItem.innerHTML = `
            <select>
                <option>英语</option>
                <option>日语</option>
                <option>韩语</option>
                <option>法语</option>
                <option>德语</option>
            </select>
            <select>
                <option>流利</option>
                <option>熟练</option>
                <option>一般</option>
                <option>基础</option>
            </select>
            <button class="remove-btn" onclick="removeLanguage(this)">删除</button>
        `;
        languageList.appendChild(languageItem);
    }
}

// 移除语言
function removeLanguage(button) {
    const languageItem = button.closest('.language-item');
    if (languageItem) {
        languageItem.remove();
    }
}

// 生成简历 - 真实API调用
async function generateResume() {
    saveCurrentStepData();
    
    showLoading('正在生成简历...', 'AI正在为您制作专业简历');
    
    try {
        // 创建简历数据
        const formData = new FormData();
        
        // 创建一个临时的简历文件（如果没有上传文件）
        if (!uploadedResumeFile) {
            const resumeText = createResumeText();
            const blob = new Blob([resumeText], { type: 'text/plain' });
            formData.append('resume', blob, 'generated_resume.txt');
        } else {
            formData.append('resume', uploadedResumeFile);
        }
        
        // 添加职位描述（如果有的话）
        const description = `根据用户信息生成简历：
姓名：${resumeData.basicInfo?.name || ''}
期望职位：${resumeData.basicInfo?.targetPosition || ''}
技能：${skills.join(', ')}`;
        
        formData.append('description', description);
        
        const response = await fetch('/generate-by-description', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showSection('result-section');
            displayResumePreview(result);
            showMessage('简历生成成功！', 'success');
        } else {
            showMessage(result.message || '生成简历失败', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('生成简历失败:', error);
        showMessage('生成简历失败: ' + error.message, 'error');
    }
}

// 创建简历文本
function createResumeText() {
    let resumeText = '';
    
    if (resumeData.basicInfo) {
        resumeText += `姓名: ${resumeData.basicInfo.name}\n`;
        resumeText += `邮箱: ${resumeData.basicInfo.email}\n`;
        resumeText += `电话: ${resumeData.basicInfo.phone}\n`;
        resumeText += `期望职位: ${resumeData.basicInfo.targetPosition}\n`;
        if (resumeData.basicInfo.summary) {
            resumeText += `个人简介: ${resumeData.basicInfo.summary}\n`;
        }
        resumeText += '\n';
    }
    
    if (resumeData.experience && resumeData.experience.length > 0) {
        resumeText += '工作经验:\n';
        resumeData.experience.forEach(exp => {
            resumeText += `- ${exp['公司名称'] || ''} ${exp['职位名称'] || ''}\n`;
            if (exp['描述您的主要工作内容和成就']) {
                resumeText += `  ${exp['描述您的主要工作内容和成就']}\n`;
            }
        });
        resumeText += '\n';
    }
    
    if (resumeData.education && resumeData.education.length > 0) {
        resumeText += '教育背景:\n';
        resumeData.education.forEach(edu => {
            resumeText += `- ${edu['学校名称'] || ''} ${edu['专业名称'] || ''} ${edu.select || ''}\n`;
        });
        resumeText += '\n';
    }
    
    if (skills.length > 0) {
        resumeText += `技能: ${skills.join(', ')}\n`;
    }
    
    return resumeText;
}

// 绑定文件上传事件
function bindFileUpload() {
    const resumeFileInput = document.getElementById('resume-file');
    if (resumeFileInput) {
        resumeFileInput.addEventListener('change', handleFileUpload);
    }
}

// 处理文件上传 - 真实API调用
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件类型
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('请上传PDF、Word或TXT格式的简历文件', 'error');
        return;
    }
    
    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showMessage('文件大小不能超过10MB', 'error');
        return;
    }
    
    uploadedResumeFile = file;
    
    showLoading('正在分析简历...', 'AI正在解析您的简历内容');
    
    try {
        const formData = new FormData();
        formData.append('resume', file);
        
        const response = await fetch('/upload-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            // 显示分析结果
            showAnalysisResult();
            showMessage('简历分析完成！', 'success');
        } else {
            showMessage(result.message || '分析失败', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('文件上传失败:', error);
        showMessage('分析失败: ' + error.message, 'error');
    }
}

// 显示分析结果
function showAnalysisResult() {
    const uploadZone = document.getElementById('upload-zone');
    const analysisResult = document.getElementById('analysis-result');
    
    if (uploadZone && analysisResult) {
        uploadZone.style.display = 'none';
        analysisResult.style.display = 'block';
        
        // 添加建议
        addSuggestions();
    }
}

// 添加优化建议
function addSuggestions() {
    const suggestionList = document.getElementById('suggestion-list');
    if (suggestionList) {
        const suggestions = [
            {
                type: 'warning',
                title: '关键词密度不足',
                content: '建议在工作经验中增加更多与目标职位相关的关键词'
            },
            {
                type: 'success',
                title: '格式规范',
                content: '简历格式整洁，结构清晰'
            },
            {
                type: 'info',
                title: '技能展示',
                content: '可以添加更多技术技能和项目经验'
            }
        ];
        
        suggestionList.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <div class="suggestion-icon ${suggestion.type}">
                    ${suggestion.type === 'warning' ? '⚠️' : suggestion.type === 'success' ? '✅' : 'ℹ️'}
                </div>
                <div class="suggestion-content">
                    <h5>${suggestion.title}</h5>
                    <p>${suggestion.content}</p>
                </div>
            </div>
        `).join('');
    }
}

// 绑定标签页切换
function bindTabSwitching() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

// 切换标签页
function switchTab(tabName) {
    // 更新按钮状态
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });
    
    // 更新内容显示
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName + '-tab') {
            content.classList.add('active');
        }
    });
}

// 初始化拖拽上传
function initDragAndDrop() {
    const uploadZone = document.getElementById('upload-zone');
    if (uploadZone) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const resumeFileInput = document.getElementById('resume-file');
                if (resumeFileInput) {
                    resumeFileInput.files = files;
                    handleFileUpload({ target: { files: files } });
                }
            }
        });
    }
}

// 分析职位匹配 - 真实API调用
async function analyzeJobMatch() {
    const jobDescription = document.getElementById('job-description').value;
    const jobUrl = document.getElementById('job-url').value;
    
    if (!jobDescription && !jobUrl) {
        showMessage('请输入职位描述或职位链接', 'error');
        return;
    }
    
    if (!uploadedResumeFile) {
        showMessage('请先上传简历文件', 'error');
        return;
    }
    
    showLoading('正在分析职位匹配度...', 'AI正在分析职位要求与您的简历匹配度');
    
    try {
        const formData = new FormData();
        formData.append('resume', uploadedResumeFile);
        
        let endpoint = '';
        if (jobDescription) {
            formData.append('description', jobDescription);
            endpoint = '/generate-by-description';
        } else if (jobUrl) {
            formData.append('url', jobUrl);
            endpoint = '/generate-by-url';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showMatchResult(result);
            showMessage('匹配度分析完成！', 'success');
        } else {
            showMessage(result.message || '分析失败', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('职位匹配分析失败:', error);
        showMessage('分析失败: ' + error.message, 'error');
    }
}

// 显示匹配结果
function showMatchResult(result) {
    const matchResult = document.getElementById('match-result');
    if (matchResult) {
        matchResult.style.display = 'block';
        
        // 更新匹配分数
        const matchScore = document.getElementById('match-score');
        if (matchScore && result.match_score) {
            matchScore.textContent = Math.round(result.match_score * 100);
        }
        
        // 添加职位建议
        addJobSuggestions(result);
    }
}

// 添加职位建议
function addJobSuggestions(result) {
    const jobSuggestions = document.getElementById('job-suggestions');
    if (jobSuggestions) {
        let suggestions = [];
        
        if (result.suggestions) {
            suggestions = result.suggestions.map(suggestion => ({
                title: '优化建议',
                content: suggestion
            }));
        }
        
        if (result.ats_suggestions) {
            suggestions = suggestions.concat(result.ats_suggestions.map(suggestion => ({
                title: 'ATS优化',
                content: suggestion
            })));
        }
        
        if (suggestions.length === 0) {
            suggestions = [
                {
                    title: '增加技术关键词',
                    content: '在简历中突出与职位相关的技术关键词'
                },
                {
                    title: '量化工作成果',
                    content: '用具体数字描述项目成果和工作成就'
                },
                {
                    title: '突出相关经验',
                    content: '重点描述与目标职位相关的项目经验'
                }
            ];
        }
        
        jobSuggestions.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <div class="suggestion-icon info">💡</div>
                <div class="suggestion-content">
                    <h5>${suggestion.title}</h5>
                    <p>${suggestion.content}</p>
                </div>
            </div>
        `).join('');
    }
}

// 应用优化建议
async function applyOptimizations() {
    if (!uploadedResumeFile) {
        showMessage('请先上传简历文件', 'error');
        return;
    }
    
    showLoading('正在应用优化建议...', '正在根据建议优化您的简历');
    
    try {
        const formData = new FormData();
        formData.append('resume', uploadedResumeFile);
        formData.append('description', '优化简历内容，提高ATS通过率');
        
        const response = await fetch('/generate-by-description', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showSection('result-section');
            displayResumePreview(result);
            showMessage('简历优化完成！', 'success');
        } else {
            showMessage(result.message || '优化失败', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('简历优化失败:', error);
        showMessage('优化失败: ' + error.message, 'error');
    }
}

// 定制简历
async function customizeResume() {
    const jobDescription = document.getElementById('job-description').value;
    const jobUrl = document.getElementById('job-url').value;
    
    if (!jobDescription && !jobUrl) {
        showMessage('请输入职位描述或职位链接', 'error');
        return;
    }
    
    if (!uploadedResumeFile) {
        showMessage('请先上传简历文件', 'error');
        return;
    }
    
    showLoading('正在定制简历...', '正在根据职位要求定制您的简历');
    
    try {
        const formData = new FormData();
        formData.append('resume', uploadedResumeFile);
        
        let endpoint = '';
        if (jobDescription) {
            formData.append('description', jobDescription);
            endpoint = '/generate-by-description';
        } else if (jobUrl) {
            formData.append('url', jobUrl);
            endpoint = '/generate-by-url';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showSection('result-section');
            displayResumePreview(result);
            showMessage('简历定制完成！', 'success');
        } else {
            showMessage(result.message || '定制失败', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('简历定制失败:', error);
        showMessage('定制失败: ' + error.message, 'error');
    }
}

// 显示简历预览
function displayResumePreview(result) {
    const previewContent = document.getElementById('preview-content');
    if (previewContent) {
        let previewHTML = `
            <div class="resume-preview">
                <h3>简历预览</h3>
        `;
        
        if (result) {
            previewHTML += `
                <div class="result-summary">
                    <div class="score-display">
                        <span class="score-number">${Math.round((result.match_score || 0.85) * 100)}</span>
                        <span class="score-label">分</span>
                    </div>
                    <div class="result-info">
                        <p><strong>生成时间:</strong> ${new Date(result.timestamp || Date.now()).toLocaleString()}</p>
                        <p><strong>文件名:</strong> ${result.generated_file || '简历文件'}</p>
                    </div>
                </div>
            `;
            
            if (result.suggestions && result.suggestions.length > 0) {
                previewHTML += `
                    <div class="suggestions-summary">
                        <h4>优化建议</h4>
                        <ul>
                            ${result.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        } else {
            previewHTML += `
                <div class="preview-placeholder">
                    <p>📄 您的简历已生成完成</p>
                    <p>点击预览按钮查看完整简历</p>
                </div>
            `;
        }
        
        previewHTML += `
            </div>
        `;
        
        previewContent.innerHTML = previewHTML;
    }
}

// 加载模板列表
async function loadTemplates() {
    try {
        const response = await fetch('/templates');
        if (response.ok) {
            const data = await response.json();
            // 这里可以更新模板选择界面
            console.log('可用模板:', data.templates);
        }
    } catch (error) {
        console.error('加载模板失败:', error);
    }
}

// 预览简历
function previewResume() {
    showMessage('简历预览功能开发中...', 'info');
}

// 编辑简历
function editResume() {
    showMessage('简历编辑功能开发中...', 'info');
}

// 下载简历
function downloadResume(format) {
    showMessage(`正在准备${format.toUpperCase()}格式下载...`, 'info');
}

// 生成分享链接
function generateShareLink() {
    showMessage('分享链接生成功能开发中...', 'info');
}

// 邮件发送
function sendByEmail() {
    showMessage('邮件发送功能开发中...', 'info');
}

// 显示加载动画
function showLoading(title, subtitle) {
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtitle = document.getElementById('loading-subtitle');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        
        if (loadingText) loadingText.textContent = title;
        if (loadingSubtitle) loadingSubtitle.textContent = subtitle;
    }
}

// 隐藏加载动画
function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // 添加样式
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: 600;
        z-index: 1001;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    
    // 根据类型设置背景色
    switch(type) {
        case 'success':
            messageEl.style.background = '#10b981';
            break;
        case 'error':
            messageEl.style.background = '#ef4444';
            break;
        case 'warning':
            messageEl.style.background = '#f97316';
            break;
        default:
            messageEl.style.background = '#6366f1';
    }
    
    document.body.appendChild(messageEl);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                messageEl.remove();
            }, 300);
        }
    }, 3000);
}

// 清空表单数据
function clearFormData() {
    resumeData = {};
    skills = [];
    uploadedResumeFile = null;
    
    // 清空所有输入框
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.type !== 'file') {
            input.value = '';
        }
    });
    
    // 清空技能标签
    const skillsContainer = document.getElementById('skills-tags');
    if (skillsContainer) {
        skillsContainer.innerHTML = '';
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .dragover {
        border-color: #6366f1 !important;
        background-color: rgba(99, 102, 241, 0.1) !important;
    }
    
    .skill-tag {
        display: inline-flex;
        align-items: center;
        background: #6366f1;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.875rem;
    }
    
    .skill-tag .remove-btn {
        background: none;
        border: none;
        color: white;
        margin-left: 0.5rem;
        cursor: pointer;
        font-size: 1.2rem;
        line-height: 1;
    }
    
    .suggestion-item {
        display: flex;
        align-items: flex-start;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    .suggestion-icon {
        margin-right: 0.75rem;
        font-size: 1.25rem;
    }
    
    .suggestion-content h5 {
        margin: 0 0 0.25rem 0;
        font-weight: 600;
    }
    
    .suggestion-content p {
        margin: 0;
        color: #6b7280;
        font-size: 0.875rem;
    }
    
    .result-summary {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .score-display {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-right: 2rem;
    }
    
    .score-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #10b981;
    }
    
    .score-label {
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    .result-info p {
        margin: 0.25rem 0;
        color: #374151;
    }
    
    .suggestions-summary {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 0.75rem;
    }
    
    .suggestions-summary h4 {
        margin: 0 0 1rem 0;
        color: #1f2937;
    }
    
    .suggestions-summary ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .suggestions-summary li {
        margin-bottom: 0.5rem;
        color: #4b5563;
    }
`;
document.head.appendChild(style);