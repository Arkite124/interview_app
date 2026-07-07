// src/layouts/QaLayout.jsx — 사내 문서 QA 4모드 탭 (RAG/채팅/구조화 평가/병렬 응답)

import { NavLink, Outlet } from "react-router-dom";

const TABS = [
  { to: "rag", label: "📚 RAG 문서 QA" },
  { to: "chat", label: "💬 기본 채팅" },
  { to: "structured", label: "📊 답변 평가" },
  { to: "parallel", label: "🔀 병렬 응답" },
];

function QaLayout() {
  return (
    <section className="mx-auto max-w-5xl">
      <div className="mb-6">
        <p className="text-sm font-semibold text-blue-600">Doc QA</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          사내 문서 QA 챗봇
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          LangChain LCEL + LangGraph + Chroma RAG 기반 4가지 응답 모드입니다.
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-2 rounded-2xl bg-white p-2 shadow-sm ring-1 ring-slate-200">
        {TABS.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            className={({ isActive }) =>
              `rounded-xl px-4 py-2 text-sm font-medium transition ${
                isActive
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </div>

      <Outlet />
    </section>
  );
}

export default QaLayout;
