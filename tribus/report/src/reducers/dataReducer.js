import ReadFiles from '../utils/readFiles';

const initData = ReadFiles()

const parsePlotTypes = (obj) => {
    const names = Object.keys(obj)
    const typenamelists = names.map(nm => nm.split("_"))
    const samplenames = typenamelists.map(sn => sn.slice(0,-1)).map(sn => sn.join("_"))
    const unique_sns = [...new Set(samplenames)]
    const all = {}
    unique_sns.forEach(sn =>{
        const tnl = names.filter(n => n.includes(sn))
        const split_tnl = tnl.map(tn => tn.split("_"))
        const tns = split_tnl.map(tn => tn[tn.length - 1])
        all[sn] = tns
    })
    return(all)
}

const parseSampleNames = (obj) => {
    const names = Object.keys(obj)
    const samplenamelists = names.map(nm => nm.split("_"))
    const samplenames = samplenamelists.map(sn => sn.slice(0,-1))
    const joinednames = samplenames.map(sn => sn.join('_'))
    const uniques = [...new Set(joinednames)]
    return(uniques)
}

const initialState = {
    data:initData,
    plot_types:parsePlotTypes(initData),
    sample_names:parseSampleNames(initData)
}

const dataReducer = (state = initialState, action) => {
    switch(action.type) {
        default:
            return state
    }
}

export default dataReducer