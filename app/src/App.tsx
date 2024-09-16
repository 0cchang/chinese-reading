import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [allChars, setChars] = useState([]);
  const [chinese, setChinese] = useState("");
  const [english, setEnglish] = useState("");
  const [c_id, setC_id] = useState(0);
  const [newEnglish, setNewEnglish] = useState("");

  useEffect(() => {
    fetchChars();
  }, []);

  const fetchChars = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/chars/");
      const data = await response.json();
      setChars(data);
    } catch (err) {
      console.log(err);
    }
  };

  const addChar = async () => {
    const charData = {
      chinese,
      english,
      c_id,
    };
    try {
      const response = await fetch("http://127.0.0.1:8000/api/chars/create", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(charData),
      });

      const data = await response.json();
      setChars((prev) => [...prev, data]);
    } catch (err) {
      console.log(err);
    }
  };

  const updateEnglish = async (pk, c_id, chinese) => {
    const charData = {
      chinese,
      c_id,
      english: newEnglish,
    };
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/chars/${pk}`, {
        method: "PUT",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(charData),
      });

      const data = await response.json();
      setChars((prev) => 
        prev.map((charMap) => {
          if (charMap.id === pk) {
            return data;
          } else {
            return charMap;
          }
        })
      );
    } catch (err) {
      console.log(err);
    }
  };

  const deleteCharMap = async (pk) => {
    try{
      const response = await fetch(`http://127.0.0.1:8000/api/chars/${pk}`, {
        method: "DELETE",
      });
      setChars((prev) => prev.filter((charMap) => charMap.id !== pk));
    } catch (err) {
      console.log(err);
    }
  };
  return (
    <>
      <h1>Chinese Reading</h1>
      <div>
        <input type="text" placeholder="char" onChange={(e) => setChinese(e.target.value)} />
        <input type="text" placeholder="english" onChange={(e) => setEnglish(e.target.value)} />
        <input type="number" placeholder="choose id" onChange={(e) => setC_id(Number(e.target.value))} />
        <button onClick={addChar}>Submit</button>
      </div>
      {allChars.map((charMap) => (
        <div key={charMap.id}>
          <p>chinese: {charMap.chinese}</p>
          <p>english: {charMap.english}</p>
          <input 
            type="text" 
            placeholder="new definition" 
            onChange={(e) => setNewEnglish(e.target.value)} 
          />
          <button onClick={() => updateEnglish(charMap.id, charMap.c_id, charMap.chinese)}>change</button>
          <p>id: {charMap.c_id}</p>
          <button onClick={() => deleteCharMap(charMap.id)}> Delete</button>
        </div>
      ))}
    </>
  );
}

export default App;
