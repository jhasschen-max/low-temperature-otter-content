// Handle download requests from content script

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action !== 'downloadScreenshot') return;

  // Generate filename with timestamp
  const filename = `youtube-screenshot-${Date.now()}.png`;

  // Download the image
  chrome.downloads.download({
    url: message.dataUrl,
    filename: filename,
    saveAs: false
  });
});
