import { Inter } from "next/font/google";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  const params = useSearchParams();
  const router = useRouter();

  const [query, setQuery] = useState("");
  const [author, setAuthor] = useState("");
  const [stem, setStem] = useState(true);
  const [removestop, setRemovestop] = useState(true);
  const [weighting, setWeighting] = useState("tfidf");
  const [similarity, setSimilarity] = useState("cosine");
  const [weights, setWeights] = useState("1341");

  const [numDocs, setNumDocs] = useState(5);
  const [docId, setDocId] = useState("");

  const [docs, setDocs] = useState([]);

  const handleSearch = (
    query,
    author,
    stem,
    removestop,
    weighting,
    similarity,
    weights,
    numDocs
  ) => {
    console.log(author);
    fetch(
      `http://127.0.0.1:5000/search?query=${query}&author=${author}&stem=${stem}&remove=${removestop}&weighting=${weighting}&similarity=${similarity}&weights=${weights}&count=${numDocs}`
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

      if (query) setQuery(query);
      if (author) setAuthor(author);
      if (stem) setStem(stem);
      if (removestop) setRemovestop(removestop);
      if (weighting) setWeighting(weighting);
      if (similarity) setSimilarity(similarity);
      if (weights) setWeights(weights);
      if (numDocs) setNumDocs(numDocs);

      handleSearch(
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
          className="text-center text-lg py-4 border-b hover:cursor-pointer"
          onClick={() => router.push("/")}
        >
          Doc Search Engine
        </h1>
        <h2 className="text-center border-b py-1 bg-gray-100">
          Tip: click the doc ID to copy search URL (jumps to doc position) to
          clipboard.
        </h2>
        <div className="h-12 flex items-center justify-center mt-1">
          <input
            type="text"
            placeholder="Enter your query here"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="border rounded p-1 text-center mr-2"
          />
          <input
            type="text"
            placeholder="Enter the author here"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="border rounded p-1 text-center mr-2"
          />
          <button
            onClick={() =>
              handleSearch(
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
            className="border rounded py-1 px-2 text-center mr-2 bg-blue-500 text-white hover:bg-blue-700 hover:text-white transition"
          >
            Search
          </button>
        </div>
        <div className="h-8 flex items-center justify-center border-dashed border-b pb-2">
          <input
            type="checkbox"
            name="stem"
            value={stem}
            onChange={(e) => setStem(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Stem?</label>
          <input
            type="checkbox"
            name="remove"
            value={removestop}
            onChange={(e) => setRemovestop(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Remove stopwords?</label>
          <select
            name="weighting"
            value={weighting}
            onChange={(e) => setWeighting(e.target.value)}
            className="mr-2 border rounded text-sm text-center"
          >
            <option value="tf">Raw TF</option>
            <option value="tfidf">TF-IDF</option>
            <option value="boolean">Boolean</option>
          </select>
          <select
            name="similarity"
            value={similarity}
            onChange={(e) => setSimilarity(e.target.value)}
            className="mr-2 border rounded text-sm text-center"
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
            className="border rounded text-sm text-center mr-2"
          >
            <option value="1111">1,1,1,1</option>
            <option value="1341">1,3,4,1</option>
            <option value="1114">1,1,1,4</option>
          </select>
          <input
            type="text"
            placeholder="Number of docs"
            value={numDocs}
            onChange={(e) => setNumDocs(e.target.value)}
            className="border rounded text-sm text-center mr-2 w-36"
          />
        </div>
        <div className="py-2 flex justify-center border-b border-dashed">
          <input
            type="text"
            placeholder="Doc ID"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            className="text-center border rounded mr-2 p-1 w-16"
          />
          <button
            onClick={() => handleFindDoc(docId)}
            className="border rounded py-1 px-2 text-center mr-2 bg-blue-500 text-white hover:bg-blue-700 hover:text-white transition"
          >
            Find Doc
          </button>
        </div>
        <div className="mt-1">
          {docs.map((doc) => (
            <div key={doc.id} id={doc.id} className="px-4 py-2">
              <div className="flex items-center">
                <div className="mr-2 w-12 h-12 flex justify-center items-center rounded bg-blue-400 text-white">
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
                <div className="">
                  <div className="">{doc.title}</div>
                  <div className="text-[14px]">{doc.author}</div>
                </div>
              </div>
              <p className="text-sm mt-2">{doc.abstract}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
