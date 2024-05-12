import { Inter } from "next/font/google";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  const params = useSearchParams();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [query, setQuery] = useState("");
  const [author, setAuthor] = useState("");
  const [stem, setStem] = useState(true);
  const [removestop, setRemovestop] = useState(true);
  const [weighting, setWeighting] = useState("tfidf");
  const [similarity, setSimilarity] = useState("cosine");
  const [weights, setWeights] = useState("114");

  const [numDocs, setNumDocs] = useState(5);
  const [docId, setDocId] = useState("");

  const [docs, setDocs] = useState([]);

  const handleSearch = (
    title,
    query,
    author,
    stem,
    removestop,
    weighting,
    similarity,
    weights,
    numDocs
  ) => {
    fetch(
      `http://127.0.0.1:5000/search?title=${title}&query=${query}&author=${author}&stem=${stem}&remove=${removestop}&weighting=${weighting}&similarity=${similarity}&weights=${weights}&count=${numDocs}`
    )
      .then((response) => response.json())
      .then(setDocs)
      .catch((error) => console.error(error));
  };

  const handleFindDoc = (docId) => {
    fetch(`http://127.0.0.1:5000/doc?id=${docId}`)
      .then((response) => response.json())
      .then(setDocs)
      .catch((error) => console.error(error));
  };

  const scrolltoHash = (id) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({
      behavior: "smooth",
      inline: "nearest",
    });
  };

  useEffect(() => {
    if (params.size) {
      const title = params.get("title") || "";
      const query = params.get("query") || "";
      const author = params.get("author") || "";
      const stem = params.get("stem") ? params.get("stem") === "true" : true;
      const removestop = params.get("remove")
        ? params.get("remove") === "true"
        : true;
      const weighting = params.get("weighting") || "tfidf";
      const similarity = params.get("similarity") || "cosine";
      const weights = params.get("weights") || "1341";
      const numDocs = params.get("count") || "5";

      if (title) setTitle(title);
      if (query) setQuery(query);
      if (author) setAuthor(author);
      if (stem) setStem(stem);
      if (removestop) setRemovestop(removestop);
      if (weighting) setWeighting(weighting);
      if (similarity) setSimilarity(similarity);
      if (weights) setWeights(weights);
      if (numDocs) setNumDocs(numDocs);

      handleSearch(
        title,
        query,
        author,
        stem,
        removestop,
        weighting,
        similarity,
        weights,
        numDocs
      );
    }
  }, [params]);

  useEffect(() => {
    if (params.size === 0 && window.location.hash !== "") {
      const docId = window.location.hash.slice(1);
      setDocId(docId);
      handleFindDoc(docId);
      scrolltoHash(docId);
    }
  }, [params]);

  useEffect(() => {
    scrolltoHash(window.location.hash.slice(1));
  }, [docs]);

  return (
    <main className={`flex justify-center min-h-screen ${inter.className}`}>
      <div className="bg-white w-[800px]">
        <h1
          className="py-4 text-lg text-center border-b hover:cursor-pointer"
          onClick={() => router.push("/")}
        >
          Hopkins Search Engine
        </h1>
        <h2 className="py-1 text-center bg-gray-100 border-b">
          Tip: click the doc ID to copy search URL (jumps to doc position) to
          clipboard.
        </h2>
        <div className="flex items-center justify-center h-12 mt-1">
          <input
            type="text"
            placeholder="Enter the title here"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
          <input
            type="text"
            placeholder="Enter your query here"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
          <input
            type="text"
            placeholder="Enter the author here"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
          <button
            onClick={() =>
              handleSearch(
                title,
                query,
                author,
                stem,
                removestop,
                weighting,
                similarity,
                weights,
                numDocs
              )
            }
            className="px-2 py-1 mr-2 text-center text-white transition bg-blue-500 border rounded hover:bg-blue-700 hover:text-white"
          >
            Search
          </button>
        </div>
        <div className="flex items-center justify-center h-8 pb-2 border-b border-dashed">
          <input
            type="checkbox"
            name="stem"
            checked={stem}
            onChange={(e) => setStem(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Stem?</label>
          <input
            type="checkbox"
            name="remove"
            checked={removestop}
            onChange={(e) => setRemovestop(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Remove stopwords?</label>
          <select
            name="weighting"
            value={weighting}
            onChange={(e) => setWeighting(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="tf">Raw TF</option>
            <option value="tfidf">TF-IDF</option>
            <option value="boolean">Boolean</option>
          </select>
          <select
            name="similarity"
            value={similarity}
            onChange={(e) => setSimilarity(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="cosine">Cosine</option>
            <option value="jaccard">Jaccard</option>
            <option value="dice">Dice</option>
            <option value="overlap">Overlap</option>
          </select>
          <select
            name="weights"
            value={weights}
            onChange={(e) => setWeights(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="131">1,3,1</option>
            <option value="114">1,1,4</option>
            <option value="111">1,1,1</option>
          </select>
          <input
            type="text"
            placeholder="Number of docs"
            value={numDocs}
            onChange={(e) => setNumDocs(e.target.value)}
            className="mr-2 text-sm text-center border rounded w-36"
          />
        </div>
        <div className="flex justify-center py-2 border-b border-dashed">
          <input
            type="text"
            placeholder="Doc ID"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            className="w-16 p-1 mr-2 text-center border rounded"
          />
          <button
            onClick={() => handleFindDoc(docId)}
            className="px-2 py-1 mr-2 text-center text-white transition bg-blue-500 border rounded hover:bg-blue-700 hover:text-white"
          >
            Find Doc
          </button>
        </div>
        <div className="mt-1">
          {docs.map((doc) => (
            <div key={doc.id} id={doc.id} className="px-4 py-2">
              <div className="flex items-center">
                <div className="flex items-center justify-center flex-none w-12 h-12 mr-2 text-white bg-blue-400 rounded">
                  <Link
                    href={`#${doc.id}`}
                    onClick={() => {
                      navigator.clipboard.writeText(
                        `http://localhost:3000/?query=${query}&author=${author}&stem=${stem}&remove=${removestop}&weighting=${weighting}&similarity=${similarity}&weights=${weights}#${doc.id}`
                      );
                    }}
                    className="transition hover:underline"
                  >
                    {doc.id}
                  </Link>
                </div>
                <div>
                  <a href={doc.url} className="text-blue-700 hover:underline">
                    {doc.title}
                  </a>
                  <div className="text-[14px]">{doc.author}</div>
                </div>
              </div>
              <p className="mt-2 text-sm">{doc.body + "..."}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
