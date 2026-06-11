import { useState } from "react";
import { readResumeText } from "../utils/readResumeText";
import { analyzeResume } from "../api/resumeApi";

function ResumePage() {
  const [resumeText, setResumeText] = useState("");
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];

    setErrorMessage("");
    setResult("");

    if (!file) {
      setResumeText("");
      setFileName("");
      return;
    }

    try {
      const text = await readResumeText(file);
      setResumeText(text);
      setFileName(file.name);
    } catch (error) {
      setResumeText("");
      setFileName("");
      setErrorMessage(error.message);
    }
  };

  const handleAnalyzeClick = async () => {
    if (!resumeText.trim()) {
      setErrorMessage("분석할 자기소개서 내용을 입력하거나 txt 파일을 업로드하세요.");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage("");
      setResult("");

      const data = await analyzeResume(resumeText);
      setResult(data.result);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-6xl">
      <div className="mb-8">
        <p className="text-sm font-semibold text-blue-600">Resume Review</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          자소서 첨삭
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          txt 파일을 업로드하거나 내용을 직접 입력한 뒤 AI 첨삭을 요청하세요.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
          <div className="mb-6">
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              자기소개서 txt 파일 업로드
            </label>

            <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-blue-400 hover:bg-blue-50">
              <input
                type="file"
                accept=".txt,text/plain"
                onChange={handleFileChange}
                className="hidden"
              />

              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
                ↑
              </div>

              <p className="text-sm font-semibold text-slate-700">
                클릭해서 txt 파일 선택
              </p>
              <p className="mt-1 text-xs text-slate-500">
                현재는 .txt 파일만 지원합니다.
              </p>
            </label>

            {fileName && (
              <div className="mt-3 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700 ring-1 ring-emerald-200">
                업로드된 파일: <span className="font-semibold">{fileName}</span>
              </div>
            )}
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="block text-sm font-semibold text-slate-700">
                자기소개서 내용
              </label>

              <span className="text-xs text-slate-400">
                {resumeText.length.toLocaleString()}자
              </span>
            </div>

            <textarea
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              placeholder="자기소개서 내용을 입력하세요."
              rows={16}
              className="w-full resize-y rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />
          </div>

          {errorMessage && (
            <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
              {errorMessage}
            </div>
          )}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={handleAnalyzeClick}
              disabled={isLoading}
              className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {isLoading ? "분석 중..." : "첨삭 요청"}
            </button>

            <button
              type="button"
              onClick={() => {
                setResumeText("");
                setResult("");
                setErrorMessage("");
                setFileName("");
              }}
              className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              초기화
            </button>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 className="text-lg font-bold text-slate-900">작성 팁</h2>

            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
              <li className="rounded-xl bg-slate-50 p-3">
                <span className="font-semibold text-slate-800">상황</span>과{" "}
                <span className="font-semibold text-slate-800">문제</span>를
                먼저 짧게 설명하세요.
              </li>
              <li className="rounded-xl bg-slate-50 p-3">
                본인이 실제로 한 행동을 중심으로 적으세요.
              </li>
              <li className="rounded-xl bg-slate-50 p-3">
                가능하면 숫자나 결과로 성과를 보여주세요.
              </li>
            </ul>
          </div>

          <div className="rounded-3xl bg-slate-900 p-6 text-white shadow-sm">
            <h2 className="text-lg font-bold">첨삭 기준</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              구조, 구체성, 직무 연관성, 불필요한 표현을 중심으로 피드백을
              받을 수 있게 설계합니다.
            </p>
          </div>
        </aside>
      </div>

      {result && (
        <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900">첨삭 결과</h2>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              AI Feedback
            </span>
          </div>

          <pre className="whitespace-pre-wrap rounded-2xl bg-slate-50 p-5 text-sm leading-7 text-slate-700 ring-1 ring-slate-200">
            {result}
          </pre>
        </div>
      )}
    </section>
  );
}

export default ResumePage;