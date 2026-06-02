interface ConnectionStatusProps {
  status: "loading" | "ok" | "degraded" | "error";
  worldengineBase?: string;
  healthText?: string;
}

export function ConnectionStatus(props: ConnectionStatusProps) {
  const labelClass = props.status === "ok" ? "status-ok" : "status-bad";

  return (
    <section className="page-card">
      <h2>WorldEngine 连接状态</h2>
      <div className="status-row">
        <span className={labelClass}>status: {props.status}</span>
        <span>WE API: {props.worldengineBase || "—"}</span>
      </div>
      {props.healthText ? <p>{props.healthText}</p> : null}
    </section>
  );
}
