/**
 * resume.js - 이력서 관리 화면 전환 및 업로드 로직 (jQuery)
 */

$(function() {
    // 1. 화면 요소 참조
    const $dashboardView = $('#dashboard-view');
    const $uploadView = $('#upload-view');
    const $resumeList = $('#resume-list');
    const $dropZone = $('#dropZone');
    const $fileInput = $('#fileInput');
    
    // 2. 화면 전환 이벤트
    
    // [등록 버튼 클릭] -> 리스트 숨김, 업로드 표시
    $('#go-upload-btn').on('click', function() {
        $dashboardView.fadeOut(200, function() {
            $uploadView.fadeIn(200);
        });
    });

    // [뒤로가기 버튼 클릭] -> 업로드 숨김, 리스트 표시
    $('#back-to-list-btn').on('click', function() {
        $uploadView.fadeOut(200, function() {
            $dashboardView.fadeIn(200);
        });
    });

    // 3. 파일 업로드 기능 (드래그 앤 드롭 & 클릭)

    // 클릭 시 파일 탐색기 열기
    $dropZone.on('click', function(e) {
        if (e.target !== this) return;
        $fileInput.trigger('click');
    });

    $fileInput.on('click', function(e) {
        e.stopPropagation();
    });

    // 드래그 효과 (진입)
    $dropZone.on('dragover dragenter', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('drag-over');
    });

    // 드래그 효과 (이탈/드롭)
    $dropZone.on('dragleave drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('drag-over');
    });

    // 파일 드롭 시 처리
    $dropZone.on('drop', function(e) {
        // jQuery 이벤트 래퍼에서 원본 이벤트(originalEvent)에 접근하여 dataTransfer 추출
        const files = e.originalEvent.dataTransfer.files;
        if(files.length > 0) handleFileUpload(files[0]);
    });

    // 파일 선택(input) 시 처리
    $fileInput.on('change', function(e) {
        // this는 DOM 요소를 가리키므로 표준 JS 속성인 .files 사용 가능
        if(this.files.length > 0) handleFileUpload(this.files[0]);
    });

    // 4. 파일 업로드 처리 및 카드 생성 함수
    function handleFileUpload(file) {
        // 시뮬레이션 알림
        alert(`'${file.name}' 파일을 분석 중입니다...`);

        setTimeout(() => {
            // 파일 용량 계산 (MB)
            const fileSize = (file.size / 1024 / 1024).toFixed(1) + 'MB';
            
            // 새 카드 HTML 생성
            const newCardHtml = createResumeCard(file.name, fileSize);

            // 리스트 맨 앞에 추가 (.prepend)
            $resumeList.prepend(newCardHtml);

            // 카운트 업데이트
            updateTotalCount();

            // 화면 전환 (업로드 -> 리스트)
            $uploadView.fadeOut(200, function() {
                $dashboardView.fadeIn(200);
                
                // 새 카드 강조 효과
                const $newCard = $resumeList.find('.resume-card').first();
                $newCard.css({
                    'border': '2px solid var(--primary-orange)',
                    'background-color': '#fff5f0'
                });
                
                setTimeout(() => {
                    $newCard.css({
                        'border': '1px solid #eee',
                        'background-color': '#fff'
                    });
                }, 1500);
            });
            
            // 입력값 초기화
            $fileInput.val('');

        }, 800);
    }

    // 5. 이력서 카드 HTML 생성기
    function createResumeCard(fileName, fileSize) {
        return `
            <div class="resume-card">
                <div class="card-header">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <div class="file-name">${fileName}</div>
                        <div class="file-meta">${fileSize} • 방금 전</div>
                    </div>
                    <button class="delete-btn">🗑️</button>
                </div>
                <div class="divider"></div>
                <div class="info-row">
                    <span class="info-label">분석 상태</span>
                    <span class="info-value" style="color:var(--primary-orange)">분석 대기중</span>
                </div>
                <div class="info-row">
                    <span class="info-label">경력</span>
                    <span class="info-value">-</span>
                </div>
                <div class="tech-tags">
                    <span class="tag tag-more">분석 필요</span>
                </div>
                <div class="stats-area">
                    <div class="stats-row">
                        <span>연습 횟수</span>
                        <span class="stats-val">0회</span>
                    </div>
                    <div class="stats-row">
                        <span>마지막 사용</span>
                        <span>-</span>
                    </div>
                </div>
                <button class="detail-btn">상세 보기 &gt;</button>
            </div>
        `;
    }

    // 6. 삭제 버튼 기능 (이벤트 위임 사용)
    $(document).on('click', '.delete-btn', function(e) {
        e.stopPropagation();
        if(confirm("이력서를 삭제하시겠습니까?")) {
            $(this).closest('.resume-card').fadeOut(300, function() {
                $(this).remove();
                updateTotalCount();
            });
        }
    });

    // 7. 총 개수 업데이트
    function updateTotalCount() {
        const count = $('.resume-card').length;
        $('#total-count-txt').text(`${count}개의 이력서가 등록되어 있습니다.`);
    }
});