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
 * 格式化法條內容（處理換行）
 */
function formatLawContent(content) {
    // 將 # 符號替換為換行
    return content
        .split('#')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => `<p style="margin-bottom: 0.5rem;">${line}</p>`)
        .join('');
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

    // 綁定收合事件
    setupToggleEvents();
}

/**
 * 按考卷分組題目
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

    // 按題號分組（因為一個題目可能有多個選項匹配）
    const questionsByNumber = {};
    questions.forEach(q => {
        if (!questionsByNumber[q.question_number]) {
            questionsByNumber[q.question_number] = {
                question_number: q.question_number,
                question_text: q.question_text,
                options: []
            };
        }
        questionsByNumber[q.question_number].options.push(q);
    });

    const questionsHtml = Object.values(questionsByNumber).map(question => {
        return renderQuestion(reportId, question);
    }).join('');

    return `
        <div style="margin-bottom: 2rem;">
            <h3 style="color: var(--primary-700); font-size: 1.25rem; margin-bottom: 1rem;">
                ${year} 年 - ${subject}
            </h3>
            ${questionsHtml}
        </div>
    `;
}

/**
 * 渲染單個題目（可收合）
 */
function renderQuestion(reportId, question) {
    const questionId = `${reportId}-${question.question_number}`;

    const optionsHtml = question.options.map(opt => `
        <div style="background: var(--neutral-50); border: 1px solid var(--neutral-200); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; gap: 0.75rem; margin-bottom: 0.5rem;">
                <div style="flex-shrink: 0; width: 2rem; height: 2rem; background: var(--primary-500); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                    ${opt.option_letter}
                </div>
                <div style="flex: 1; padding-top: 0.125rem;">
                    ${opt.option_text}
                </div>
            </div>
            <div style="margin-left: 2.75rem; color: var(--neutral-600); font-size: 0.875rem;">
                相似度：${UIUtils.formatPercentage(opt.similarity)}
            </div>
        </div>
    `).join('');

    return `
        <div class="question-card">
            <div class="question-header" onclick="toggleQuestion('${questionId}')">
                <div class="question-number">題 ${question.question_number}</div>
                <div class="question-toggle" id="toggle-${questionId}">▼</div>
            </div>
            <div class="question-body" id="body-${questionId}">
                <div class="question-text">${question.question_text}</div>
                <div style="margin-top: 1.5rem;">
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: var(--neutral-600); margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em;">
                        匹配的選項
                    </h4>
                    ${optionsHtml}
                </div>
            </div>
        </div>
    `;
}

/**
 * 設定收合/展開事件
 */
function setupToggleEvents() {
    // 所有題目預設收合
    document.querySelectorAll('.question-body').forEach(body => {
        body.classList.remove('expanded');
    });

    document.querySelectorAll('.question-toggle').forEach(toggle => {
        toggle.classList.add('collapsed');
    });
}

/**
 * 切換題目展開/收合
 */
function toggleQuestion(questionId) {
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
