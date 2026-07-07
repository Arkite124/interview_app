// src/components/qa/SourceList.jsx — RAG 출처 카드 (source/page/snippet)

export default function SourceList({ sources }) {
  if (!sources?.length) {
    return (
      <p className="mt-3 text-xs text-slate-400">
        이번 답변에 연결된 출처가 없습니다.
      </p>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400">
        📎 출처 ({sources.length}건)
      </p>

      {sources.map((src, index) => (
        <details
          key={`${src.source}-${index}`}
          className="rounded-xl bg-slate-50 p-3 text-xs ring-1 ring-slate-200"
        >
          <summary className="cursor-pointer font-semibold text-slate-700">
            {src.source} (p.{src.page})
          </summary>
          <p className="mt-2 leading-5 text-slate-600">{src.snippet}</p>
        </details>
      ))}
    </div>
  );
}
