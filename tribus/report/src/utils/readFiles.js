// TODO: use raw-loader to read the files and create a webpack?
// TODO: read only the file names to an array and only read the files
// when a plot requiring the data is created?

const ReadFiles = () => {
    const context = require.context('../data/plot_data/', true, /.json$/);
    const all = {};
    context.keys().forEach((key) => {
        const fileName = key.replace('./', '');
        const resource = require(`../data/plot_data/${fileName}`);
        const namespace = fileName.replace('.json', '');
        all[namespace] = JSON.parse(JSON.stringify(resource));
 
    });
    return(all);
}

export default ReadFiles