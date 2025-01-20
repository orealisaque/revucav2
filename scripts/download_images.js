const https = require('https');
const fs = require('fs');
const path = require('path');

const images = [
    {
        url: 'https://source.unsplash.com/1920x1080/?nightlife',
        filename: 'hero-placeholder.jpg'
    },
    {
        url: 'https://source.unsplash.com/1280x720/?party',
        filename: 'promo-placeholder.jpg'
    },
    {
        url: 'https://source.unsplash.com/1280x720/?club',
        filename: 'video-poster.jpg'
    }
];

// Cria o diretório se não existir
const imagesDir = path.join(__dirname, '../static/images');
if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
}

// Baixa cada imagem
images.forEach(image => {
    const file = fs.createWriteStream(path.join(imagesDir, image.filename));
    https.get(image.url, response => {
        response.pipe(file);
        file.on('finish', () => {
            file.close();
            console.log(`Downloaded ${image.filename}`);
        });
    }).on('error', err => {
        fs.unlink(file);
        console.error(`Error downloading ${image.filename}:`, err.message);
    });
}); 