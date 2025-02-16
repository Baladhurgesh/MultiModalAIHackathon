chrome.commands.onCommand.addListener((command) => {
  if (command === "capture-screenshot")
  {
    captureScreenshot();
  }
});

async function captureScreenshot()
{
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    // Check if the URL is permitted
    const currentTab = tabs[0];
    if (!isPermittedUrl(currentTab.url))
    {
      console.error("Cannot capture screenshot of this page due to Chrome security restrictions");
      return;
    }

    // First inject html2canvas
    chrome.scripting.executeScript(
      {
        target: { tabId: currentTab.id },
        files: ['html2canvas.min.js']
      },
      () => {
        if (chrome.runtime.lastError)
        {
          console.error('Script injection failed:', chrome.runtime.lastError.message);
          return;
        }
        
        // Add a small delay to ensure html2canvas is loaded
        setTimeout(() => {
          chrome.scripting.executeScript(
            {
              target: { tabId: currentTab.id },
              function: takeScreenshot,
            },
            (injectionResults) => {
              if (chrome.runtime.lastError)
              {
                console.error(chrome.runtime.lastError.message);
                return;
              }
              if (injectionResults && injectionResults[0])
              {
                const screenshotDataUrl = injectionResults[0].result;
                sendScreenshot(screenshotDataUrl);
              }
              else
              {
                console.error('Failed to capture screenshot');
              }
            }
          );
        }, 100);  // 100ms delay
      }
    );
  });
}

function isPermittedUrl(url)
{
  // Check if the URL is a restricted one
  return !url.startsWith('chrome://') && 
         !url.startsWith('chrome-extension://') &&
         !url.startsWith('chrome-search://') &&
         !url.startsWith('chrome-devtools://') &&
         !url.startsWith('file://') &&
         !url.startsWith('edge://') &&    // For Edge browser
         !url.startsWith('about:') &&     // For Firefox
         !url.startsWith('data:');
}

function takeScreenshot()
{
  return new Promise((resolve, reject) => {
    // Get only the visible viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    html2canvas(document.documentElement, {
      useCORS: true,
      allowTaint: true,
      width: viewportWidth,
      height: viewportHeight,
      windowWidth: viewportWidth,
      windowHeight: viewportHeight,
      x: window.scrollX,
      y: window.scrollY,
      scale: window.devicePixelRatio,
      logging: true,
      backgroundColor: null
    }).then(canvas => {
      resolve(canvas.toDataURL('image/png'));
    }).catch(err => {
      console.error('Screenshot error:', err);
      reject(err);
    });
  });
}

async function sendScreenshot(screenshotDataUrl)
{
  const apiUrl = await getApiUrl();

  if (!apiUrl)
  {
    console.error("API URL not set. Please set it in the extension options.");
    return;
  }

  fetch(apiUrl,
  {
    method: 'POST',
    headers:
    {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: screenshotDataUrl })
  })
  .then(response => response.json())
  .then(data => console.log('Screenshot sent:', data))
  .catch(error => console.error('Error sending screenshot:', error));
}

async function getApiUrl()
{
  return new Promise((resolve) => {
    chrome.storage.sync.get(['apiUrl'], (result) => {
      resolve(result.apiUrl || '');
    });
  });
} 