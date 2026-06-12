import { useState } from "react";
import { requestResumeQuestions } from "../api/resumeApi";

function ResumePage() {
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [questionCount, setQuestionCount] = useState(5);
  const [questions, setQuestions] = useState([]);
  const [toolCalls, setToolCalls] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];

    setErrorMessage("");
    setQuestions([]);
    setToolCalls([]);

    if (!file) {
      setUploadedFileName("");
      setResumeText("");
      return;
    }

    if (file.type !== "text/plain" && !file.name.endsWith(".txt")) {
      setErrorMessage("txt 파일만 업로드할 수 있습니다.");
      setUploadedFileName("");
      setResumeText("");
      return;
    }

    try {
      const text = await file.text();

      setUploadedFileName(file.name);
      setResumeText(text);
    } catch {
      setErrorMessage("파일을 읽는 중 오류가 발생했습니다.");
      setUploadedFileName("");
      setResumeText("");
    }
  };

const handleAnalyze = async () => {
  setErrorMessage("");

  if (!resumeText.trim()) {
    setErrorMessage("먼저 자기소개서 txt 파일을 업로드하세요.");
    return;
  }

  if (questionCount < 3 || questionCount > 10) {
    setErrorMessage("질문 수는 3개 이상 10개 이하로 선택해 주세요.");
    return;
  }

  setIsLoading(true);

  try {
    const result = await requestResumeQuestions({
      resumeText,
      questionCount,
    });

    setQuestions(result.questions || []);
    setToolCalls(result.tool_calls || []);
  } catch (error) {
    console.error(error);

    setErrorMessage(
      error instanceof Error
        ? error.message
        : "이력서 기반 질문 생성 중 오류가 발생했습니다."
    );
  } finally {
    setIsLoading(false);
  }
};

  return (
    <section className="mx-auto max-w-4xl">
      <div className="mb-8">
        <p className="text-sm font-semibold text-blue-600">Resume</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          이력서 분석
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          txt 파일을 업로드하면 이력서 또는 자기소개서 내용을 바탕으로
          면접 질문을 생성합니다.
        </p>
      </div>

      <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
        <div className="space-y-6">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              자기소개서 txt 파일 업로드
            </label>

            <input
              type="file"
              accept=".txt,text/plain"
              onChange={handleFileChange}
              className="block w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
            />

            {uploadedFileName && (
              <p className="mt-2 text-xs text-slate-500">
                업로드된 파일: {uploadedFileName}
              </p>
            )}

            <p className="mt-2 text-xs leading-5 text-slate-500">
              utf-8로 저장된 .txt 파일을 업로드하세요.
            </p>
          </div>

          {resumeText ? (
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                파일 내용 미리보기
              </label>

              <textarea
                value={resumeText}
                readOnly
                rows={10}
                className="w-full resize-y rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-800 outline-none"
              />

              <p className="mt-2 text-xs text-slate-500">
                총 {resumeText.length.toLocaleString()}자
              </p>
            </div>
          ) : (
            <div className="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500 ring-1 ring-slate-200">
              txt 파일을 업로드하면 내용이 표시됩니다.
            </div>
          )}

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              생성할 질문 수
            </label>

            <input
              type="number"
              min="3"
              max="10"
              value={questionCount}
              onChange={(event) =>
                setQuestionCount(Number(event.target.value))
              }
              className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />

            <p className="mt-2 text-xs leading-5 text-slate-500">
              백엔드 기준으로 3개 이상 10개 이하만 가능합니다.
            </p>
          </div>

          {errorMessage && (
            <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
              {errorMessage}
            </div>
          )}

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={isLoading || !resumeText.trim()}
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {isLoading ? "질문 생성 중..." : "이력서 기반 질문 생성"}
          </button>
        </div>
      </div>

      {questions.length > 0 && (
        <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
          <h2 className="text-xl font-bold text-slate-900">
            생성된 면접 질문
          </h2>

          <ol className="mt-4 space-y-3">
            {questions.map((question, index) => (
              <li
                key={`${question}-${index}`}
                className="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-800 ring-1 ring-slate-200"
              >
                <span className="font-semibold text-blue-600">
                  {index + 1}.{" "}
                </span>
                {question}
              </li>
            ))}
          </ol>
        </div>
      )}

      {toolCalls.length > 0 && (
        <details className="mt-6 rounded-3xl bg-slate-900 p-6 text-white shadow-sm">
          <summary className="cursor-pointer text-lg font-bold">
            Function Calling 확인 데이터
          </summary>

          <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-800 p-4 text-xs leading-5 text-slate-200">
            {JSON.stringify(toolCalls, null, 2)}
          </pre>
        </details>
      )}
    </section>
  );
}

export default ResumePage;