import React from 'react';
import { FaCommentDots } from 'react-icons/fa';

interface Props {
  onClick: () => void;
}

const ChatBubble: React.FC<Props> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-8 right-8 bg-blue-600 text-white w-16 h-16 rounded-full flex items-center justify-center shadow-lg hover:bg-blue-700 transition-transform transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      aria-label="Open chat"
    >
      <FaCommentDots size={28} />
    </button>
  );
};

export default ChatBubble; 