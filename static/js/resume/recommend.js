/**
 * 이력서 분석 시작 함수
 */
function startAnalysis() {
    // 1. 필요한 요소들을 가져옵니다.
    const resumeSelect = document.getElementById("resumeSelect");
    
    // ✅ 에러 원인: 여기서 selectedResumeId 변수를 확실하게 선언해야 합니다.
    const selectedResumeId = resumeSelect.value; 
    const companyUrl = document.getElementById("companyUrl").value;
    const companyStack = document.getElementById("companyStack").value;

    // 2. 검증: 이력서 선택 여부 확인
    if (!selectedResumeId) {
        alert("분석할 이력서를 선택해 주세요.");
        resumeSelect.focus();
        return;
    }

    // 3. 검증: 회사 URL 입력 여부 확인
    if (!companyUrl.trim()) {
        alert("회사 URL을 입력해 주세요.");
        document.getElementById("companyUrl").focus();
        return;
    }

    // 4. UI 전환: 입력 폼 숨기고 로딩 영역 표시
    document.getElementById("inputForm").style.display = "none";
    document.getElementById("loadingArea").style.display = "block";
    document.getElementById("resultArea").style.display = "none";

    // 5. API 호출 (POST /feedback)
    fetch('/feedback', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json' 
        },
        body: JSON.stringify({
            resume_id: parseInt(selectedResumeId), // 숫자로 변환
            company_url: companyUrl,
            companyStack: companyStack
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || '서버 응답 실패'); });
        }
        return response.json();
    })
    .then(data => {
        // 6. 결과 렌더링 함수 호출
        renderFeedbackResult(data);

        // 7. UI 전환: 결과 표시
        document.getElementById("loadingArea").style.display = "none";
        document.getElementById("resultArea").style.display = "block";
    })
    .catch(error => {
        alert("분석 중 오류가 발생했습니다: " + error.message);
        console.error("Analysis Error:", error);
        
        // 에러 시 다시 입력 폼으로 복구
        document.getElementById("loadingArea").style.display = "none";
        document.getElementById("inputForm").style.display = "block";
    });
}

/**
 * 분석 결과 데이터를 화면에 주입하는 함수
 */
function renderFeedbackResult(data) {
    const strengthsContent = document.getElementById('strengthsContent');
    const improvementsContent = document.getElementById('improvementsContent');

    // 강점 데이터 주입
    if (data.strengths && data.strengths.length > 0) {
        let strengthsHtml = '';
        data.strengths.forEach(item => {
            strengthsHtml += `
                <div class="result-item" style="margin-top: 10px; border-bottom: 1px dashed #eee; padding-bottom: 10px;">
                    <p style="font-weight: bold; color: #2c3e50;">• ${item.title}</p>
                    <p style="font-size: 0.9em; color: #666; margin-left: 10px;">${item.description}</p>
                </div>`;
        });
        strengthsContent.innerHTML = strengthsHtml;
    }

    // 보완점 데이터 주입
    if (data.improvements && data.improvements.length > 0) {
        let improvementsHtml = '';
        data.improvements.forEach(item => {
            improvementsHtml += `
                <div class="result-item" style="margin-top: 10px; border-bottom: 1px dashed #eee; padding-bottom: 10px;">
                    <p style="font-weight: bold; color: #e67e22;">• ${item.title}</p>
                    <p style="font-size: 0.9em; color: #666; margin-left: 10px;">${item.description}</p>
                </div>`;
        });
        improvementsContent.innerHTML = improvementsHtml;
    }
}