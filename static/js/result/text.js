/**
 * text.js - 오디오 플레이어 및 텍스트 하이라이트 로직 (jQuery version)
 */

$(function() {
    let isPlaying = false;
    let currentTime = 0;
    const totalDuration = 40; // 40초 시뮬레이션
    let playInterval;

    const $playBtn = $('#playBtn');
    const $progressFill = $('#progressFill');
    const $progressHead = $('#progressHead');
    const $timeDisplay = $('#timeDisplay');
    const $progressContainer = $('#progressContainer');
    const $sentences = $('.script-sentence');

    /**
     * 재생/일시정지 토글
     */
    window.togglePlay = function() {
        isPlaying ? pauseAudio() : playAudio();
    };

    function playAudio() {
        isPlaying = true;
        $playBtn.text('❚❚');
        playInterval = setInterval(() => {
            currentTime += 0.1;
            if (currentTime >= totalDuration) {
                currentTime = totalDuration;
                pauseAudio();
            }
            updateUI();
        }, 100);
    }

    function pauseAudio() {
        isPlaying = false;
        $playBtn.text('▶');
        clearInterval(playInterval);
    }

    /**
     * 문장 클릭 시 해당 위치로 이동
     * @param {number} time - 이동할 시간(초)
     */
    window.seekToSentence = function(time) {
        currentTime = time;
        updateUI();
        if (!isPlaying) playAudio();
    };

    /**
     * 진행바 클릭 시 이동
     */
    $progressContainer.on('click', function(e) {
        const width = $(this).width();
        const clickX = e.offsetX;
        const percent = clickX / width;
        
        currentTime = percent * totalDuration;
        updateUI();
    });

    /**
     * UI 업데이트 (진행바, 시간, 하이라이트)
     */
    function updateUI() {
        const percent = (currentTime / totalDuration) * 100;
        $progressFill.css('width', percent + '%');
        $progressHead.css('left', percent + '%');
        
        // 시간 텍스트 업데이트
        const currMin = Math.floor(currentTime / 60);
        const currSec = Math.floor(currentTime % 60);
        const totalMin = Math.floor(totalDuration / 60);
        const totalSec = Math.floor(totalDuration % 60);
        
        const timeString = 
            `${currMin.toString().padStart(2, '0')}:${currSec.toString().padStart(2, '0')} / ` +
            `${totalMin.toString().padStart(2, '0')}:${totalSec.toString().padStart(2, '0')}`;
        
        $timeDisplay.text(timeString);

        // 현재 시간에 따른 문장 하이라이트 활성화
        $sentences.removeClass('active');
        if (currentTime < 10) {
            $sentences.eq(0).addClass('active');
        } else if (currentTime < 25) {
            $sentences.eq(1).addClass('active');
        } else {
            $sentences.eq(2).addClass('active');
        }
    }
});