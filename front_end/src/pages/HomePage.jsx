import { Link } from "react-router-dom";

function HomePage() {
  return (
    <section className="mx-auto max-w-5xl">
      <div className="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-slate-200">
        <div className="bg-linear-to-br from-blue-600 to-indigo-700 px-8 py-12 text-white md:px-12">
          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-blue-100">
            AI Resume & Interview Coach
          </p>

          <h1 className="max-w-3xl text-3xl sm:text-2xl md:text-4xl font-bold tracking-tight">
            자기소개서에서 나오는 면접 질문 및 직무별 면접 질의응답들을 피드백 받아 보세요.
          </h1>

          <p className="mt-5 max-w-2xl text-base leading-7 text-blue-100">
            txt 파일을 업로드하여 예상 질문을 생성합니다.
          </p>

          <div className="mt-8">
            <Link
              to="/resume"
              className="inline-flex items-center rounded-xl bg-white px-5 py-3 text-sm font-semibold text-blue-700 shadow-sm transition hover:bg-blue-50"
            >
              예상 질문 분석 시작하기 &gt;
            </Link>
          </div>
        </div>

        <div className="grid gap-4 p-6 md:grid-cols-3 md:p-8">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              1
            </div>
            <h2 className="font-semibold">파일 업로드</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              txt 자기소개서 파일을 선택하면 내용을 자동으로 읽어옵니다.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700">
              2
            </div>
            <h2 className="font-semibold">내용 수정</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              읽어온 내용을 textarea에서 바로 수정하고 보완할 수 있습니다.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              3
            </div>
            <h2 className="font-semibold">AI 첨삭 요청</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              FastAPI 백엔드로 내용을 보내고 첨삭 결과를 화면에 표시합니다.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HomePage;