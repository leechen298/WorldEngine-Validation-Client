import { useMemo, useState } from "react";
import { RuntimeConsole } from "./pages/RuntimeConsole";
import { SessionLibrary } from "./pages/SessionLibrary";

export default function App() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeTitle] = useState("WorldEngine Validation Client");

  const pageTitle = useMemo(() => activeTitle, [activeTitle]);

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>{pageTitle}</h1>
      </header>
      {activeSessionId ? (
        <RuntimeConsole sessionId={activeSessionId} onBack={() => setActiveSessionId(null)} />
      ) : (
        <SessionLibrary onOpenSession={setActiveSessionId} />
      )}
    </main>
  );
}
