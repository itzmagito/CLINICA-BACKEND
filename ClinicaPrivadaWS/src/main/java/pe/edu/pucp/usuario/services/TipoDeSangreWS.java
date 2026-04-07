
package pe.edu.pucp.usuario.services;

import jakarta.jws.WebService;
import jakarta.ejb.Stateless;
import jakarta.jws.WebMethod;
import jakarta.jws.WebParam;
import java.util.ArrayList;
import pe.edu.pucp.usuario.bo.TipoDeSangreBO;
import pe.edu.pucp.usuario.model.TipoDeSangre;

@Stateless
@WebService(serviceName = "TipoDeSangreWS", targetNamespace = "http://services.pucp.edu.pe")

public class TipoDeSangreWS {
    private TipoDeSangreBO boTipoSangre;
 
    @WebMethod(operationName = "listarTipoSangre")
    public ArrayList<TipoDeSangre> listarTipoSangre(){
        boTipoSangre = new TipoDeSangreBO();
        return boTipoSangre.listarTodos();
    }
}
