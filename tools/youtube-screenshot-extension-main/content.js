// Inject screenshot button into YouTube player controls

// Capture the video frame and return as data URL
function captureVideoFrame() {
  const video = document.querySelector('video');
  if (!video) return null;

  // Create canvas matching video dimensions
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Draw current video frame to canvas
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Return as PNG data URL
  return canvas.toDataURL('image/png');
}

// Copy image to clipboard
//It’s async because clipboard operations are asynchronous and require permissions.
async function copyToClipboard(dataUrl) {
  try {
    const response = await fetch(dataUrl);
    const blob = await response.blob();
    await navigator.clipboard.write([
      new ClipboardItem({ 'image/png': blob })
    ]);
    // console.log('Screenshot copied to clipboard');
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
  }
}

function injectButton() {
  // Check if button already exists
  if (document.getElementById('yt-screenshot-btn')) return;

  // Find the right controls container (left side of player controls)
  const controls = document.querySelector('.ytp-left-controls');
  if (!controls) return;

  // Create the button
  const btn = document.createElement('button');
  btn.id = 'yt-screenshot-btn';
  btn.textContent = 'Screenshot';
  btn.title = 'Take screenshot of video and copy to clipboard';
  
  // Style to match YouTube controls
  btn.style.cssText = `
    background: transparent;
    border: none;
    color: white;
    font-size: 12px;
    padding: 0 8px;
    cursor: pointer;
    height: 100%;
    opacity: 0.9;
    font-family: Roboto, Arial, sans-serif;
  `;

  // Hover effect
  btn.onmouseenter = () => btn.style.opacity = '1';
  btn.onmouseleave = () => btn.style.opacity = '0.9';

  // Click handler - capture video frame
  btn.onclick = async (e) => {
    e.stopPropagation();
    
    // Capture the video frame
    const dataUrl = captureVideoFrame();
    if (!dataUrl) {
      console.error('No video found');
      return;
    }

    // Copy to clipboard (works because we have user gesture)
    copyToClipboard(dataUrl);

    // Send to background for download
    chrome.runtime.sendMessage({ action: 'downloadScreenshot', dataUrl });
  };

  // Insert button into controls
  controls.appendChild(btn);
}

// Watch for YouTube's dynamic content loading
const observer = new MutationObserver(() => {
  injectButton();
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Initial injection attempt
injectButton();
