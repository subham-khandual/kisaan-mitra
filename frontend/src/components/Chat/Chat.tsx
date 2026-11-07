import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./KrushiMitra.module.css";
import Picker from "emoji-picker-react";
import assistantAvatar from "../../assets/krushi_avatar.png";
import chatBg from "../../assets/chat_bg.png";

const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY;

const Chat = () => {
  const navigate = useNavigate();

  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  const recognition = useRef<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Farmer Data
  const farmerData = {
    state: "Odisha",
    district: "Bhubaneswar",
    soilType: "Loamy",
    landArea: "2 Acres",
    irrigation: "Available",
    preferredCrops: ["Rice", "Wheat"],
  };

  // Agriculture AI Config
  const agroConfig = {
    identity: {
      name: "KrushiMitra",
      creator: "LogicLoom Team",
      language: "Hindi/Odia/English",
      traits: [
        "helpful",
        "smart",
        "farmer-friendly",
        "professional",
      ],

      capabilities: [
        "Crop recommendation 🌾",
        "Mandi price updates 📈",
        "Weather forecast 🌦️",
        "Pest detection 🐛",
        "Fertilizer guidance 🌱",
        "Government schemes 🏛️",
        "Soil analysis 🌍",
        "Seed recommendation 🌱",
        "Irrigation advice 💧",
        "Nearby agriculture shops 🚜",
      ],
    },

    systemMessage: `
You are KrushiMitra, a smart multilingual agriculture AI assistant for Indian farmers.

RULES:
1. Speak mostly in Hinglish.
2. Be friendly and farmer-focused.
3. Give practical farming advice.
4. Help with:
   - Crop recommendation
   - Mandi prices
   - Weather
   - Fertilizers
   - Pest control
   - Irrigation
   - Government schemes

5. If user asks about crops:
   Ask:
   - Soil type
   - Season
   - Water availability
   - Location

6. Keep answers simple and short.

Farmer Data:
${JSON.stringify(farmerData, null, 2)}
`,
  };

  // Text To Speech
  const speakText = useCallback((text: string) => {
    if (!window.speechSynthesis) return;

    const synth = window.speechSynthesis;

    if (synth.speaking) {
      synth.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "hi-IN";
    utterance.rate = 1;
    utterance.pitch = 1;

    synth.speak(utterance);
  }, []);

  // Load Messages
  useEffect(() => {
    const savedMessages = localStorage.getItem("krushiMessages");

    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }

    // Speech Recognition
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      recognition.current = new SpeechRecognition();

      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-IN";

      recognition.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;

        setUserInput(transcript);
        setIsListening(false);

        sendMessage(transcript);
      };

      recognition.current.onerror = () => {
        setIsListening(false);

        setMessages((prev) => [
          ...prev,
          {
            text: "Kissan Mitra 🌾 awaaz clear nahi aayi, fir se boliye.",
            sender: "ai",
            timestamp: new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          },
        ]);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Welcome Message
  useEffect(() => {
    const welcomeMessage = {
      text: `Hi Kissan Mitra! 🌾 Main aapki pyari agriculture assistant KrushiMitra hoon. Bataiye aaj farming mein kis cheez mein madad chahiye? 🚜`,
      sender: "ai",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages([welcomeMessage]);

    setConversationHistory([
      {
        role: "assistant",
        content: welcomeMessage.text,
      },
    ]);

    speakText(
      "Hi Kissan Mitra! Main aapki pyari agriculture assistant KrushiMitra hoon. Aaj farming mein kya help chahiye?"
    );
  }, [speakText]);

  // Save Messages
  useEffect(() => {
    localStorage.setItem("krushiMessages", JSON.stringify(messages));

    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // Redirect Features
  const redirectToFeature = (input: string) => {
    const lowerInput = input.toLowerCase();

    if (lowerInput.includes("mandi")) {
      return "/prices";
    }

    if (
      lowerInput.includes("crop") ||
      lowerInput.includes("recommendation")
    ) {
      return "/crop-ai";
    }

    if (lowerInput.includes("weather")) {
      return "/weather";
    }

    if (
      lowerInput.includes("fertilizer") ||
      lowerInput.includes("npk")
    ) {
      return "/crop-ai";
    }

    if (
      lowerInput.includes("disease") ||
      lowerInput.includes("pest")
    ) {
      return "/dashboard";
    }

    if (lowerInput.includes("soil")) {
      return "/crop-ai";
    }

    if (lowerInput.includes("scheme")) {
      return "/dashboard";
    }

    if (lowerInput.includes("irrigation")) {
      return "/dashboard";
    }

    return null;
  };

  // Voice Input
  const startListening = () => {
    if (recognition.current && !isListening) {
      setIsListening(true);

      recognition.current.start();

      const listenMessage =
        "Sun rahi hoon Kissan Mitra 🌾 boliye...";

      setMessages((prev) => [
        ...prev,
        {
          text: listenMessage,
          sender: "ai",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);

      speakText(listenMessage);
    }
  };

  // Emoji
  const onEmojiClick = (emojiObject: any) => {
    setUserInput((prev) => prev + emojiObject.emoji);
    setShowEmojiPicker(false);
  };

  // File Upload
  const handleFileUpload = (event: any) => {
    const file = event.target.files[0];

    if (!file) return;

    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    setMessages((prev) => [
      ...prev,
      {
        text: `Uploaded file: ${file.name}`,
        sender: "user",
        timestamp,
      },
    ]);

    const aiReply =
      "Image receive ho gaya 🌱 Future update mein crop disease detection add hoga.";

    setMessages((prev) => [
      ...prev,
      {
        text: aiReply,
        sender: "ai",
        timestamp,
      },
    ]);

    speakText(aiReply);
  };

  // Delete Chat
  const deleteAllMessages = () => {
    if (window.confirm("Delete all chats?")) {
      localStorage.removeItem("krushiMessages");

      const clearMessage =
        "Chat successfully clear ho gaya 🌾";

      setMessages([
        {
          text: clearMessage,
          sender: "ai",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);

      speakText(clearMessage);
    }
  };

  // Quick Replies
  const handleQuickReply = (query: string) => {
    setUserInput(query);
    sendMessage(query);
  };

  // Send Message
  const sendMessage = async (input = userInput) => {
    if (!input.trim()) return;

    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const userMessage = {
      text: input,
      sender: "user",
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);

    setUserInput("");

    setIsTyping(true);

    try {
      // Redirect Feature
      const redirectPath = redirectToFeature(input);

      if (redirectPath) {
        const redirectMessage =
          "Aapko related agriculture page pe le ja rahi hoon 🌾";

        setMessages((prev) => [
          ...prev,
          {
            text: redirectMessage,
            sender: "ai",
            timestamp: new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          },
        ]);

        speakText(redirectMessage);

        setTimeout(() => {
          navigate(redirectPath);
        }, 1000);

        setIsTyping(false);

        return;
      }

      // Build Messages
      const groqMessages = [
        {
          role: "system",
          content: agroConfig.systemMessage,
        },

        ...conversationHistory,

        {
          role: "user",
          content: input,
        },
      ];

      // API Call
      const response = await fetch(
        "https://api.groq.com/openai/v1/chat/completions",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${GROQ_API_KEY}`,
          },

          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: groqMessages,
            temperature: 0.8,
            max_tokens: 500,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("API Error");
      }

      const data = await response.json();

      let aiText =
        data.choices?.[0]?.message?.content ||
        "Kuch technical issue aa gaya 🌾";

      // Save Conversation
      setConversationHistory((prev) => [
        ...prev,

        {
          role: "user",
          content: input,
        },

        {
          role: "assistant",
          content: aiText,
        },
      ]);

      // Add AI Response
      setMessages((prev) => [
        ...prev,
        {
          text: aiText,
          sender: "ai",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);

      speakText(aiText);
    } catch (error) {
      console.log(error);

      const errorMessage =
        "Server problem aa gaya 🌾 Thodi der baad try kariye.";

      setMessages((prev) => [
        ...prev,
        {
          text: errorMessage,
          sender: "ai",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);

      speakText(errorMessage);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      {/* HEADER */}
      <div className={styles.header}>
        <img
          src={assistantAvatar}
          alt="KrushiMitra"
          className={styles.avatar}
        />

        <div className={styles.headerInfo}>
          <span className={styles.headerTitle}>
            KrushiMitra 🌾
          </span>

          <span className={styles.headerSubtitle}>
            Smart Agriculture AI Assistant
          </span>
        </div>

        <button
          onClick={deleteAllMessages}
          className={styles.deleteButton}
        >
          🗑️
        </button>
      </div>

      {/* CHAT AREA */}
      <div
        className={styles.chatBox}
        style={{
          backgroundImage: `url(${chatBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundColor: 'var(--bg-card)', // fallback
          backgroundBlendMode: 'overlay', // ensures text is readable if you add an overlay color
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            className={styles[`${msg.sender}Message`]}
          >
            {msg.text}

            <span className={styles.timestamp}>
              {msg.timestamp}
            </span>
          </div>
        ))}

        {isTyping && (
          <div className={styles.typing}>
            KrushiMitra typing...
          </div>
        )}

        {isListening && (
          <div className={styles.typing}>
            🎤 Sun rahi hoon...
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* QUICK REPLIES */}
      <div className={styles.quickReplies}>
        <button
          onClick={() =>
            handleQuickReply("Crop recommendation")
          }
        >
          Crop Recommendation
        </button>

        <button
          onClick={() =>
            handleQuickReply("Mandi prices")
          }
        >
          Mandi Prices
        </button>

        <button
          onClick={() => handleQuickReply("Weather")}
        >
          Weather
        </button>

        <button
          onClick={() =>
            handleQuickReply("Fertilizer")
          }
        >
          Fertilizer
        </button>
      </div>

      {/* FOOTER */}
      <div className={styles.footer}>
        <div className={styles.inputWrapper}>
          {/* EMOJI */}
          <span
            className={styles.smileyIcon}
            onClick={() =>
              setShowEmojiPicker(!showEmojiPicker)
            }
          >
            😊
          </span>

          {showEmojiPicker && (
            <div className={styles.emojiPicker}>
              <Picker onEmojiClick={onEmojiClick} />
            </div>
          )}

          {/* FILE */}
          <label className={styles.attachmentIcon}>
            📎

            <input
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleFileUpload}
            />
          </label>

          {/* INPUT */}
          <input
            type="text"
            placeholder="Ask farming question..."
            value={userInput}
            onChange={(e) =>
              setUserInput(e.target.value)
            }
            onKeyPress={(e) =>
              e.key === "Enter" && sendMessage()
            }
            className={styles.inputField}
          />

          {/* SEND BUTTON */}
          {userInput.trim() ? (
            <button
              onClick={() => sendMessage()}
              className={styles.sendButton}
            >
              ➡️
            </button>
          ) : (
            <button
              onClick={startListening}
              disabled={isListening}
              className={styles.micButton}
            >
              {isListening ? "🎙️" : "🎤"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;
