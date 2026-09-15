import panchsetuLogo from "../../assets/panchsetu-logo.png";

function BrandLogo({ compact = false }) {
  return (
    <div className="flex flex-col items-center justify-center">
      <img
        src={panchsetuLogo}
        alt="PANCHSETU logo"
        className={compact ? "h-10 w-auto object-contain" : "h-20 w-auto object-contain"}
      />
    </div>
  );
}

export default BrandLogo;