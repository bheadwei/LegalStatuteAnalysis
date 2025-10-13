/**
 * 題目頁邏輯 - 顯示法條詳細資料和相關題目（可收合）
 */

let lawDetail = null;

/**
 * 頁面初始化
 */
document.addEventListener('DOMContentLoaded', async () => {
    const lawId = UIUtils.getUrlParam('law_id');

    if (!lawId) {
        showError('缺少法條 ID 參數');
        return;
    }

    await loadLawDetail(lawId);
});

/**
 * 載入法條詳細資料
 */
async function loadLawDetail(lawId) {
    const lawInfoSection = document.getElementById('law-info-section');
    const questionsSection = document.getElementById('questions-section');

    try {
        UIUtils.showLoading(lawInfoSection);
        UIUtils.showLoading(questionsSection);

        lawDetail = await API.getLawDetail(lawId);

        // 更新頁面標題
        document.getElementById('page-title').textContent = `${lawDetail.law_name} - ${lawDetail.article_no}`;
        document.getElementById('page-subtitle').textContent = `共 ${lawDetail.matched_count} 個匹配項目`;

        // 渲染法條資訊
        renderLawInfo();

        // 渲染相關題目
        renderQuestions();

    } catch (error) {
        UIUtils.showError(lawInfoSection, `無法載入法條資料：${error.message}`);
        console.error('載入法條詳細資料失敗:', error);
    }
}

/**
 * 渲染法條資訊卡片
 */
function renderLawInfo() {
    const lawInfoSection = document.getElementById('law-info-section');

    lawInfoSection.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">${lawDetail.law_name} ${lawDetail.article_no}</h2>
                <span class="law-category">${lawDetail.category}</span>
            </div>
            <div class="card-body">
                <div style="background: var(--neutral-50); padding: 1.5rem; border-radius: var(--radius-md); line-height: 1.8;">
                    ${formatLawContent(lawDetail.content)}
                </div>
            </div>
        </div>
    `;
}

/**
 * 格式化法條內容（條列式呈現，自動識別項目符號）
 */
function formatLawContent(content) {
    if (!content) return '';

    // 先處理 # 符號分割
    let processedContent = content.replace(/#/g, '\n');

    // 識別並在條列項目前換行
    // 匹配：一、二、三、... 或 （一）（二）... 或 1. 2. 3. ...
    processedContent = processedContent
        // 在中文數字編號前換行（一、二、三、四、五...）
        .replace(/([^。\n])(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|十三、|十四、|十五、)/g, '$1\n$2')
        // 在括號數字前換行（（一）（二）...）
        .replace(/([^。\n])(（一）|（二）|（三）|（四）|（五）|（六）|（七）|（八）|（九）|（十）)/g, '$1\n$2')
        // 在阿拉伯數字編號前換行（1. 2. 3. ...）
        .replace(/([^。\n])(\d+\.\s)/g, '$1\n$2')
        // 清理多餘空行
        .replace(/\n\s*\n/g, '\n')
        .trim();

    // 分割成行
    const lines = processedContent
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

    if (lines.length === 0) return '';

    // 渲染每一行
    const linesHtml = lines
        .map(line => {
            // 檢查是否為條列項目
            const isListItem = /^(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|（一）|（二）|（三）|（四）|（五）|\d+\.\s)/.test(line);

            if (isListItem) {
                // 條列項目：縮排 + 加粗編號
                return `<p style="margin-bottom: 0.5rem; line-height: 1.8; padding-left: 1rem; text-indent: -1rem;">${line}</p>`;
            } else {
                // 一般段落
                return `<p style="margin-bottom: 0.5rem; line-height: 1.8;">${line}</p>`;
            }
        })
        .join('');

    return linesHtml;
}

/**
 * 渲染相關題目
 */
function renderQuestions() {
    const questionsSection = document.getElementById('questions-section');

    if (!lawDetail.related_questions || lawDetail.related_questions.length === 0) {
        questionsSection.innerHTML = `
            <div class="card">
                <p style="text-align: center; color: var(--neutral-600);">
                    沒有找到相關題目
                </p>
            </div>
        `;
        return;
    }

    // 按考卷分組題目
    const questionsByReport = groupQuestionsByReport(lawDetail.related_questions);

    const questionsHtml = Object.entries(questionsByReport).map(([reportId, questions]) => {
        return renderReportQuestions(reportId, questions);
    }).join('');

    questionsSection.innerHTML = questionsHtml;
}

/**
 * 按考卷分組題目（新數據結構：每題包含所有選項）
 */
function groupQuestionsByReport(questions) {
    const grouped = {};

    questions.forEach(q => {
        if (!grouped[q.report_id]) {
            grouped[q.report_id] = [];
        }
        grouped[q.report_id].push(q);
    });

    // 按題號排序每個報告的題目
    Object.keys(grouped).forEach(reportId => {
        grouped[reportId].sort((a, b) => a.question_number - b.question_number);
    });

    return grouped;
}

/**
 * 渲染單個考卷的題目
 */
function renderReportQuestions(reportId, questions) {
    // 提取年份和科目
    const parts = reportId.split('_');
    const year = parts[0].substring(0, 3);  // 113
    const subject = parts[2];  // 民法概要

    const questionsHtml = questions.map(question => {
        return renderQuestion(reportId, question);
    }).join('');

    return `
        <div style="margin-bottom: 2rem;">
            <h3 style="color: var(--primary-700); font-size: 1.25rem; margin-bottom: 1rem; font-weight: 700;">
                📝 ${year} 年 - ${subject}
            </h3>
            ${questionsHtml}
        </div>
    `;
}

/**
 * 渲染單個題目（可收合，顯示所有選項）
 */
function renderQuestion(reportId, question) {
    const questionId = `${reportId}-${question.question_number}`;

    // 渲染所有選項
    const optionsHtml = question.all_options.map(opt => {
        // 判斷樣式
        const isCorrect = opt.is_correct;
        const matchedTarget = opt.matched_target;

        let optionClass = 'option-item';
        let badgeHtml = '';
        let similarityHtml = '';

        if (isCorrect) {
            optionClass += ' correct-option';
            badgeHtml = '<span class="correct-badge">✓ 正確答案</span>';
        }

        if (matchedTarget) {
            badgeHtml += `<span class="matched-badge">🎯 匹配此法條 (${UIUtils.formatPercentage(opt.similarity)})</span>`;
        }

        return `
            <div class="${optionClass}">
                <div style="display: flex; gap: 0.75rem; align-items: start;">
                    <div class="option-letter-circle ${isCorrect ? 'correct' : ''}">
                        ${opt.option_letter}
                    </div>
                    <div style="flex: 1;">
                        <div class="option-text">${opt.option_text}</div>
                        ${badgeHtml ? `<div class="option-badges">${badgeHtml}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    return `
        <div class="question-card-full">
            <div class="question-header-full" onclick="toggleQuestionBody('${questionId}')">
                <span class="question-number-badge">
                    題 ${question.question_number}
                    <span class="question-toggle-icon collapsed" id="toggle-${questionId}">▼</span>
                </span>
                <span class="correct-answer-info">正確答案：${question.correct_answer}</span>
            </div>
            <div class="question-body-full" id="body-${questionId}">
                <div class="question-text">${question.question_text}</div>
                <div class="options-container">
                    ${optionsHtml}
                </div>
            </div>
        </div>
    `;
}

/**
 * 切換題目展開/收合
 */
function toggleQuestionBody(questionId) {
    const body = document.getElementById(`body-${questionId}`);
    const toggle = document.getElementById(`toggle-${questionId}`);

    if (body.classList.contains('expanded')) {
        body.classList.remove('expanded');
        toggle.classList.add('collapsed');
    } else {
        body.classList.add('expanded');
        toggle.classList.remove('collapsed');
    }
}

/**
 * 顯示錯誤訊息
 */
function showError(message) {
    const lawInfoSection = document.getElementById('law-info-section');
    lawInfoSection.innerHTML = `
        <div class="card" style="background: #fee2e2; border-color: #fecaca;">
            <p style="color: #b91c1c; font-weight: 500;">❌ ${message}</p>
            <p style="color: #b91c1c; margin-top: 1rem;">
                <a href="/" class="btn btn-secondary">返回首頁</a>
            </p>
        </div>
    `;
}
