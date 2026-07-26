import { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { uploadLogFile, runDetection } from "../api/upload";

const LOG_TYPES = [
  { value: "linux_auth", label: "Linux Auth Log (SSH)" },
  { value: "apache", label: "Apache / Nginx Access Log" },
];

export default function LogUpload() {
  const [file, setFile] = useState(null);
  const [logType, setLogType] = useState("linux_auth");
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | uploading | detecting | done | error
  const [result, setResult] = useState(null);
  const [detection, setDetection] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef(null);

  const handleFile = (selected) => {
    if (!selected) return;
    setFile(selected);
    setStatus("idle");
    setResult(null);
    setDetection(null);
    setErrorMsg("");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const handleUpload = async () => {
  if (!file) return;
  setStatus("uploading");
  setErrorMsg("");
  try {
    const uploadResult = await uploadLogFile(file, logType);
    setResult(uploadResult);
    setDetection(uploadResult.detection);
    setStatus("done");
  } catch (err) {
    const detail = err?.response?.data?.message || err?.response?.data?.detail || "Upload failed.";
    setErrorMsg(typeof detail === "string" ? detail : "Upload failed.");
    setStatus("error");
  }
};


  const reset = () => {
    setFile(null);
    setResult(null);
    setDetection(null);
    setStatus("idle");
    setErrorMsg("");
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-display font-semibold text-bone">Log Analyzer</h1>
        <p className="text-sm text-slate/50 mt-1">Upload a log file to parse, ingest, and run detection.</p>
      </div>

      {/* Log type selector */}
      <div>
        <label className="block text-xs uppercase tracking-wide text-slate/50 font-mono mb-2">Log format</label>
        <select
          value={logType}
          onChange={(e) => setLogType(e.target.value)}
          className="bg-panel/50 border border-panel rounded-md px-3 py-2 text-sm font-mono text-bone focus:outline-none focus:border-amber/50 w-full"
        >
          {LOG_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors ${
          dragActive ? "border-amber bg-amber/5" : "border-panel bg-panel/30 hover:border-amber/40"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".log,.txt"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <FileText size={28} className="text-amber" />
            <p className="font-mono text-sm text-bone">{file.name}</p>
            <p className="text-xs text-slate/40">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <UploadCloud size={28} className="text-slate/40" />
            <p className="font-mono text-sm text-slate/60">Drag & drop a log file, or click to browse</p>
            <p className="text-xs text-slate/30">Supports .log and .txt files</p>
          </div>
        )}
      </div>

      {/* Action button */}
      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading" || status === "detecting"}
        className="w-full bg-amber/10 border border-amber/40 text-amber font-mono text-sm py-2.5 rounded-md hover:bg-amber/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {status === "uploading" && <><Loader2 size={16} className="animate-spin" /> Parsing log file...</>}
        {status === "detecting" && <><Loader2 size={16} className="animate-spin" /> Running detection...</>}
        {(status === "idle" || status === "error") && "Upload & Analyze"}
        {status === "done" && "Analyze Another File"}
      </button>

      {/* Error state */}
      {status === "error" && (
        <div className="flex items-start gap-2 text-rust font-mono text-sm border border-rust/30 bg-rust/10 rounded-lg p-4">
          <XCircle size={16} className="mt-0.5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Results */}
      {result && status === "done" && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-amber font-mono text-sm">
            <CheckCircle2 size={16} />
            Analysis complete
          </div>

          <div className="bg-panel/50 border border-panel rounded-lg p-5">
            <h2 className="font-display text-sm text-bone mb-3">Parse Summary</h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-display text-bone">{result.total_lines}</p>
                <p className="text-xs text-slate/50 font-mono mt-1">total lines</p>
              </div>
              <div>
                <p className="text-2xl font-display text-amber">{result.parsed_count}</p>
                <p className="text-xs text-slate/50 font-mono mt-1">parsed</p>
              </div>
              <div>
                <p className="text-2xl font-display text-slate/50">{result.unparsed_count}</p>
                <p className="text-xs text-slate/50 font-mono mt-1">unparsed</p>
              </div>
            </div>
          </div>

          {result.total_lines > 0 && result.unparsed_count / result.total_lines > 0.5 && (
  <div className="flex items-start gap-2 text-amber font-mono text-xs border border-amber/30 bg-amber/10 rounded-lg p-3">
    <XCircle size={14} className="mt-0.5 shrink-0" />
    Over half the lines in this file failed to parse. This usually means the wrong log format
    was selected — double check whether this file is actually {logType === "linux_auth" ? "an Apache/Nginx access log" : "a Linux auth log"} instead.
  </div>
)}

          {detection && (
            <div className="bg-panel/50 border border-panel rounded-lg p-5">
              <h2 className="font-display text-sm text-bone mb-3">Detection Results</h2>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-display text-bone">{detection.threats_found}</p>
                  <p className="text-xs text-slate/50 font-mono mt-1">threats found</p>
                </div>
                <div>
                  <p className={`text-2xl font-display ${detection.alerts_created > 0 ? "text-rust" : "text-slate/50"}`}>
                    {detection.alerts_created}
                  </p>
                  <p className="text-xs text-slate/50 font-mono mt-1">new alerts</p>
                </div>
                <div>
                  <p className="text-2xl font-display text-slate/50">{detection.duplicates_skipped}</p>
                  <p className="text-xs text-slate/50 font-mono mt-1">duplicates skipped</p>
                </div>
              </div>
              {detection.alerts_created > 0 && (
                <p className="text-xs text-slate/40 font-mono mt-3 text-center">
                  Check the Alerts page to investigate.
                </p>
              )}
            </div>
          )}

          <button onClick={reset} className="text-xs text-slate/50 hover:text-amber font-mono underline">
            Upload another file
          </button>
        </div>
      )}
    </div>
  );
}