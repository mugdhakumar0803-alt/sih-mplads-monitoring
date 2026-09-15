import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getGrievances, getPhotos, getWork } from "../api/client";
import PhotoUpload from "../components/PhotoVerification/PhotoUpload";
import GrievancePanel from "../components/Grievance/GrievancePanel";

function WorkDetail() {
  const { workId } = useParams();
  const navigate = useNavigate();
  const [work, setWork] = useState(null);
  const [photos, setPhotos] = useState([]);
  const [grievances, setGrievances] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getWork(workId), getPhotos(workId), getGrievances(workId)])
      .then(([workResult, photoResult, grievanceResult]) => {
        setWork(workResult);
        setPhotos(photoResult.photos);
        setGrievances(grievanceResult.grievances);
      })
      .catch((requestError) => setError(requestError.message));
  }, [workId]);

  if (error) return <div className="min-h-screen bg-gray-50 p-8 text-red-600">{error}</div>;
  if (!work) return <div className="min-h-screen bg-gray-50 p-8 text-gray-500">Loading work...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <button onClick={() => navigate(-1)} className="text-sm text-gray-400 mb-4">← Back</button>
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h1 className="text-xl font-bold text-navy">{work.title}</h1>
        <p className="text-sm text-gray-400">{work.work_id} · {work.state}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div><p className="text-xs text-gray-400">Category</p><p className="font-semibold text-navy">{work.category}</p></div>
          <div><p className="text-xs text-gray-400">Allocation</p><p className="font-semibold text-navy">₹{work.allocation_amount?.toLocaleString()}</p></div>
          <div><p className="text-xs text-gray-400">Status</p><p className="font-semibold text-navy">{work.status}</p></div>
          <div><p className="text-xs text-gray-400">Risk</p><p className="font-semibold text-navy">{work.risk_level || "Not assessed"}</p></div>
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <div className="bg-white border border-gray-200 rounded-lg p-5 mb-4">
            <p className="font-semibold text-navy text-sm mb-4">Verified Photos ({photos.length})</p>
            {photos.length === 0 ? <p className="text-sm text-gray-400">No photos uploaded yet.</p> : photos.map((photo) => <div key={photo.photo_id} className="border border-gray-200 rounded p-3 mb-2"><p className="text-sm text-navy">{photo.status}</p><p className="text-xs text-gray-400">Score: {photo.verification_score}</p></div>)}
          </div>
          <PhotoUpload workId={workId} onUpload={(photo) => setPhotos((previous) => [photo, ...previous])} />
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <p className="font-semibold text-navy text-sm mb-4">Grievances ({grievances.length})</p>
          {grievances.map((grievance) => <div key={grievance.grievance_id} className="border border-gray-200 rounded p-3 mb-2"><p className="text-xs text-gray-400">{grievance.grievance_id} · {grievance.status}</p><p className="text-sm text-gray-600">{grievance.description}</p></div>)}
          <GrievancePanel presetWorkId={workId} presetWorkTitle={work.title} />
        </div>
      </div>
    </div>
  );
}

export default WorkDetail;
