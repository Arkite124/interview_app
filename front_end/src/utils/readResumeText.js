export function readResumeText(file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      resolve("");
      return;
    }

    if (file.type !== "text/plain") {
      reject(new Error("현재는 txt 파일만 지원합니다."));
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      resolve(reader.result || "");
    };

    reader.onerror = () => {
      reject(new Error("파일을 읽는 중 오류가 발생했습니다."));
    };

    reader.readAsText(file, "UTF-8");
  });
}