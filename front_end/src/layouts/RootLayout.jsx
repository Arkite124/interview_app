import { Link, Outlet, useLocation } from "react-router-dom";

function RootLayout() {
  const location = useLocation();

  const isActive = (path) => {
    if (path === "/qa") {
      return location.pathname === path || location.pathname.startsWith("/qa/");
    }
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white px-6 py-8 shadow-sm md:block">
          <div className="mb-10">
            <p className="text-sm font-semibold text-blue-600">AI Interview</p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight">
              Interview App
            </h1>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              자소서 분석으로 면접 연습을 하고, 미리 예상 면접 질문들을 받아보세요.
            </p>
          </div>

          <nav className="space-y-2">
            <Link
              to="/"
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive("/")
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              홈
            </Link>

            <Link
              to="/resume"
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive("/resume")
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              예상 질문 생성
            </Link>

            <Link
              to="/agents"
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive("/agents")
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              면접 에이전트
            </Link>

            <Link
              to="/qa"
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive("/qa")
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              사내 문서 QA
            </Link>

            <Link
              to="/settings"
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive("/settings")
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              설정
            </Link>
          </nav>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="border-b border-slate-200 bg-white px-5 py-4 shadow-sm md:hidden">
            <div className="mb-4">
              <p className="text-sm font-semibold text-blue-600">
                AI Interview
              </p>
              <h1 className="text-xl font-bold">Interview App</h1>
            </div>

            <nav className="flex flex-wrap gap-2">
              <Link
                to="/"
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive("/")
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                홈
              </Link>

              <Link
                to="/resume"
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive("/resume")
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                자소서 첨삭
              </Link>

              <Link
                to="/agents"
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive("/agents")
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                면접 에이전트
              </Link>

              <Link
                to="/qa"
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive("/qa")
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                사내 문서 QA
              </Link>

              <Link
                to="/settings"
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive("/settings")
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                설정
              </Link>
            </nav>
          </header>

          <main className="flex-1 px-5 py-8 md:px-10 lg:px-14">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

export default RootLayout;