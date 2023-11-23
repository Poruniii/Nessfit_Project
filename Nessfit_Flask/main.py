from webpages import create_app
app = create_app()

if __name__ =='__main__': # debug tool, turn this off when going public. =False
    app.run(debug = True)