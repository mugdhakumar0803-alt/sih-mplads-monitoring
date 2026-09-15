import { useState } from "react";
import { verifyPhoto } from "../../api/client";

function PhotoUpload({ workId, onUpload }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file || !workId) return;
    setUploading(true);
    setError("");
    try {
      const verification = await verifyPhoto(workId, file);
      setResult(verification);
      onUpload?.(verification);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <form onSubmit={handleUpload} className="bg-white border border-gray-200 rounded-lg p-5">
      <p className="font-semibold text-navy text-sm mb-4">Upload Progress Photo</p>
      <input type="file" accept="image/*" capture="environment" onChange={(event) => setFile(event.target.files?.[0] || null)} disabled={uploading || result} className="text-sm mb-4 w-full" />
      {!result && <button type="submit" disabled={!file || uploading} className="bg-navy text-white px-4 py-2 rounded text-sm font-semibold disabled:opacity-40">{uploading ? "Verifying..." : "Upload & Verify"}</button>}
      {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
      {result && <div className={`border rounded p-3 mt-3 ${result.status === "verified" ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}><p className="text-sm font-semibold">{result.status}</p><p className="text-xs text-gray-500">Verification score: {result.verification_score}</p>{result.rejection_reason && <p className="text-xs text-red-600 mt-1">{result.rejection_reason}</p>}</div>}
    </form>
  );
}

export default PhotoUpload;
