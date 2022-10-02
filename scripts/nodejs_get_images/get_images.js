import { fileURLToPath } from "url";
import fetch from 'node-fetch';

// we need these functions to eval script
// but these functions are provided in https://comic.aya.click/js/nview.js
const lcRegex = /(function lc.*)/
const nnRegex = /(function nn.*)/
const mmRegex = /(function mm.*)/

// mock object to eval(script)
const mockObject = `
let document = {
    location: url,
    getElementById: () => ({
        src: ""
    })
}
const spp = () => {}`

const episode_url = process.argv?.[2] || null
const isVerbose = false

async function Request(url) {
    return fetch(url, {
        headers: {
            "Cookie": "RI=0"
        }
    })
}

function FirstOrDefault(args) {
    return args?.[0]
}

async function FetchImageAmount(url, evalScriptPrefix) {
    if (isVerbose)
        console.error(`[FetchImageAmount] [${url}] Fetching url`)

    const resp = await Request(url)
    const html = await resp.text()
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] Fetching Result: [${html}]`)

    // cut only the javaScript part
    let script = html.substring(html.indexOf('function request'))
    script = script.substring(0, script.indexOf('</script>'))
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] script = [${script}]`)

    // fetch assign img src part:
    // 
    // after split & filter the output would be like:
    //     ge(k0__0r_4av(6)+k0__0r_4av(5)).src=unescape(w1q9vcac6j+w1q9vcac6j+k0__0r_4av(4)+un_5fae6_(bg21mnh, 0, 1)+um1a2k1q9+hac6j0hp_+k0__0r_4av(3)+k0__0r_4av(2)+k0__0r_4av(3)+w1q9vcac6j+un_5fae6_(bg21mnh,1,1)+w1q9vcac6j+ti+w1q9vcac6j+i9g00mg21+w1q9vcac6j+nn(p)+e_4avn23+un_5fae6_(er3i6ho_,mm(p),3)+um1a2k1q9+k0__0r_4av(1))
    // 
    // we use replace to remove "ge(k0__0r_4av(6)+k0__0r_4av(5)).src=" part
    const IncludeSrc = el => el.includes('src=')
    const srcScript = FirstOrDefault(script.split(';').filter(IncludeSrc))?.replace(/.*\.src=/, '')
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] srcScript = [${srcScript}]`)

    const evalScript = [evalScriptPrefix, script, '(ps)'].join(';')
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] evalScript = [${evalScript}]`)

    return eval(evalScript)
}

async function FetchImageSrc(url, evalScriptPrefix) {
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] Fetching url`)

    const resp = await Request(url)
    const html = await resp.text()

    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] Fetching Result: [${html}]`)

    // cut only the javaScript part
    let script = html.substring(html.indexOf('function request'))
    script = script.substring(0, script.indexOf('</script>'))
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] script = [${script}]`)

    // fetch assign img src part:
    // 
    // after split & filter the output would be like:
    //     ge(k0__0r_4av(6)+k0__0r_4av(5)).src=unescape(w1q9vcac6j+w1q9vcac6j+k0__0r_4av(4)+un_5fae6_(bg21mnh, 0, 1)+um1a2k1q9+hac6j0hp_+k0__0r_4av(3)+k0__0r_4av(2)+k0__0r_4av(3)+w1q9vcac6j+un_5fae6_(bg21mnh,1,1)+w1q9vcac6j+ti+w1q9vcac6j+i9g00mg21+w1q9vcac6j+nn(p)+e_4avn23+un_5fae6_(er3i6ho_,mm(p),3)+um1a2k1q9+k0__0r_4av(1))
    // 
    // we use replace to remove "ge(k0__0r_4av(6)+k0__0r_4av(5)).src=" part
    const IncludeSrc = el => el.includes('src=')
    let srcScript = FirstOrDefault(script.split(';').filter(IncludeSrc))?.replace(/.*\.src=/, '')
    srcScript = `(pp => { return ${srcScript} })(p)`
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] srcScript = [${srcScript}]`)

    const evalScript = [evalScriptPrefix, script, `(${srcScript})`].join(';')
    if (isVerbose)
        console.error(`[FetchImageSrc] [${url}] evalScript = [${evalScript}]`)

    return eval(evalScript)
}

async function Run() {

    if (!episode_url) {
        return {
            status: "failed"
        }
    }

    // our target
    const url = new URL(episode_url)
    const hostname = url?.hostname

    const nviewUrl = `https://${hostname}/js/nview.js`

    // Get raw string of function lc(), nn(), mm()
    const nviewResp = await Request(nviewUrl)
    const nviewScript = await nviewResp.text()
    if (isVerbose)
        console.error(`[FetchNView] [${nviewUrl}] Fetch Result = [${nviewScript}]`)

    const lcScript = nviewScript.match(lcRegex)?.[1]
    if (isVerbose)
        console.error(`[FetchNView] [${nviewUrl}] lcScript = [${lcScript}]`)

    const nnScript = nviewScript.match(nnRegex)?.[1]
    if (isVerbose)
        console.error(`[FetchNView] [${nviewUrl}] nnScript = [${nnScript}]`)

    const mmScript = nviewScript.match(mmRegex)?.[1]
    if (isVerbose)
        console.error(`[FetchNView] [${nviewUrl}] mmScript = [${mmScript}]`)

    // we need lc(), nn(), mm(), spp() to eval script
    // for spp(), we only need to mock it since it does not matters
    const evalScriptPrefix = [mockObject, lcScript, nnScript, mmScript].join(';')
    if (isVerbose)
        console.error(`[FetchNView] [${nviewUrl}] evalScriptPrefix = [${evalScriptPrefix}]`)

    const episodeImageCount = await FetchImageAmount(url, evalScriptPrefix)
    if (isVerbose)
        console.error(`[FetchImageAmount] [${url}] episodeImageCount = [${episodeImageCount}]`)

    const tasks = [...Array(episodeImageCount).keys()]
        .map(x => x + 1)
        .map(i => FetchImageSrc(`${url}-${i}`, evalScriptPrefix))
    const taskResults = await Promise.all(tasks)

    return {
        status: 'success',
        totalAmout: episodeImageCount,
        imageSrc: taskResults.map(x => `https:${x}`)
    }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
    if (episode_url == null) {
        console.error('Please Provide episode_url!')
        console.error('example:')
        console.error(`\t node get_images.js 'https://comicabc.com/online/new-19317.html?ch=1'`)
    }
    else {
        (async () => {
            const result = await Run()
            console.log(JSON.stringify(result, null, 4))
        })();
    }
}