const NATIVE_HOST_NAME = "com.hubo.video_downloader.proxy";

function sendNativeMessage(hostName, payload) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendNativeMessage(hostName, payload, (response) => {
      const runtimeError = chrome.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }
      resolve(response);
    });
  });
}

function setActionFeedback(tabId, label, title) {
  chrome.action.setBadgeBackgroundColor({ color: label === "OK" ? "#0f9d58" : "#db4437", tabId });
  chrome.action.setBadgeText({ text: label, tabId });
  chrome.action.setTitle({ title, tabId });

  setTimeout(() => {
    chrome.action.setBadgeText({ text: "", tabId });
    chrome.action.setTitle({ title: "Queue download via Hubo Video Downloader", tabId });
  }, 30000);
}

async function capturePageHtml(tabId) {
  const results = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => document.documentElement?.outerHTML ?? ""
  });
  return results?.[0]?.result ?? "";
}

chrome.action.onClicked.addListener(async (tab) => {
  const tabId = tab?.id;
  if (!tabId || !tab?.url) {
    return;
  }

  try {
    const pageHtml = await capturePageHtml(tabId);
    const payload = {
      url: tab.url,
      pageHtml,
      pageTitle: tab.title ?? "",
      timestamp: new Date().toISOString()
    };

    const response = await sendNativeMessage(NATIVE_HOST_NAME, payload);
    const ok = !!response?.ok;
    const message = response?.message ?? (ok ? "Queued" : "Failed");

    setActionFeedback(tabId, ok ? "OK" : "ERR", message);
    console.log("Native host response:", response);
  } catch (error) {
    const message = `Native messaging failed: ${error?.message ?? String(error)}`;
    setActionFeedback(tabId, "ERR", message);
    console.error(message);
  }
});