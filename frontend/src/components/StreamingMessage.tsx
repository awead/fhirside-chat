import { useEffect, useState } from "react";

interface StreamingMessageProps {
  content: string;
  speed?: number;
  onComplete?: () => void;
}

export function StreamingMessage({
  content,
  speed = 20,
  onComplete,
}: StreamingMessageProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (displayedText.length < content.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(content.slice(0, displayedText.length + 1));
      }, speed);
      return () => clearTimeout(timeout);
    } else if (!isComplete && displayedText.length === content.length) {
      const completeTimeout = setTimeout(() => {
        setIsComplete(true);
        onComplete?.();
      }, 0);
      return () => clearTimeout(completeTimeout);
    }
  }, [displayedText, content, speed, isComplete, onComplete]);

  const skipAnimation = () => {
    setDisplayedText(content);
    setIsComplete(true);
    onComplete?.();
  };

  return (
    <div
      onClick={skipAnimation}
      onKeyDown={(e) => e.key === "Enter" && skipAnimation()}
      role="button"
      tabIndex={0}
      aria-label={content}
      className="cursor-pointer"
    >
      {displayedText}
      {!isComplete && (
        <span className="animate-pulse text-primary ml-0.5">▋</span>
      )}
    </div>
  );
}
