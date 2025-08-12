// cxaihelp.js

/**
 * Request AI Help from the /aihelp backend
 * @param {string} sourceCode - Raw Python code
 * @param {Object} options - Options for the AI engine
 * @returns {Promise<Object>} - Resolved with help data (parsed)
 */
async function requestAiHelp(sourceCode, options = {}, baseUrl = "/aihelp") {
    const payload = {
        source: sourceCode,
        options: {
            apiProvider: options.apiProvider || "dummy",
            modelName: options.modelName || "gemini-2.5-flash-lite",
            includeLong: options.includeLong !== false,
            spokenLanguage: options.spokenLanguage || "english",
            dryrun: options.dryrun === true,
            apikey: options.apikey || "" // added to support API key
        }
    };
    console.log('in requestAiHelp; options:', options)

    const res = await fetch(baseUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const json = await res.json();
    console.log('in requestAiHelp; returned json:', json)
    console.log('in requestAiHelp; returned json.data:', json.data)

    if (!res.ok || !json.metadata?.success) {
        throw new Error(json.metadata?.error || "Unknown error from AI Help service");
    }

    return json;
    //return json.data;  // AI help data
}

/**
 * Convert AI help JSON into allhelp format used by CX visualizer
 * @param {Object} data - Parsed help data from backend
 * @param {boolean} includeLong - Whether to include long help
 * @returns {Object} allhelp dictionary: { "linenum": "help", ... }
 */
function convertAiHelpDataToAllHelp(data, includeLong = true) {
    console.log('in convertAiHelpToAllHelp(); data=', data)
    const allhelp = {};

    for (const [key, val] of Object.entries(data)) {
        const helpText = includeLong && val.long
            ? `${val.short}<br><br>${val.long}`
            : val.short;

        if (key === "000") {
            allhelp["-title"] = helpText;
        } else {
            const cleanKey = key.replace(/^0+/, "");  // remove leading zeros
            allhelp[cleanKey] = helpText;
        }
    }
    console.log('in convertAiHelpToAllHelp(); allhelp=', allhelp)
    return allhelp;
}
